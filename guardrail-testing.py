import boto3
import json

# Initialize the Bedrock client
bedrock_client = boto3.client('bedrock-runtime')

# Apply 
def apply_guardrail_without_invoke_model():
    bedrock_client = boto3.client('bedrock-runtime')
    bedrock_agent_client = boto3.client('bedrock-agent-runtime')
    openai.api_key = os.environ.get("OPENAI_API_KEY")


    # User query
    query = "How can I improve AWS security for my S3 buckets?"
    
    # Step 1: Apply guardrails to the input query
    try:
        guardrail_response = bedrock_agent_client.apply_guardrail(
            guardrailIdentifier="YOUR_GUARDRAIL_ID",
            guardrailVersion="DRAFT",
            content=query,
            contentType="text/plain"
        )
        
        # Check if content was blocked
        if guardrail_response['output']['assessment']['topicPolicy']['action'] == "BLOCK":
            print("Query blocked by guardrail")
            return
            
        # Use potentially modified query
        filtered_query = guardrail_response['output']['content']
        
        # Step 2: Retrieve from Knowledge Base
        kb_response = bedrock_agent_client.retrieve(
            knowledgeBaseId="YOUR_KNOWLEDGE_BASE_ID",
            retrievalQuery={
                "text": filtered_query
            },
            retrievalConfiguration={
                "vectorSearchConfiguration": {
                    "numberOfResults": 3
                }
            }
        )
        
        # Process retrieved results
        retrieved_results = kb_response.get('retrievalResults', [])
        context = ""
        
        for i, result in enumerate(retrieved_results):
            content = result['content']['text']
            source = result.get('location', {}).get('s3Location', {}).get('uri', 'Unknown')
            context += f"\nPassage {i+1} (Source: {source}):\n{content}\n"
        
        # Step 3: Call OpenAI with retrieved context
        system_prompt = """You are a helpful assistant. Use the provided knowledge base information to answer the user's question.
If the information needed is not in the provided passages, say that you don't have enough information."""
        
        user_prompt = f"""Based on the following information from an AWS knowledge base, please answer this question:
        
Question: {filtered_query}

Knowledge Base Information:
{context}

Please provide a comprehensive answer using only the information provided above."""
        
        openai_response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=500
        )
        
        response_content = openai_response['choices'][0]['message']['content']
        
        # Step 4: Apply guardrails to the output
        output_check = bedrock_agent_client.apply_guardrail(
            guardrailIdentifier="YOUR_GUARDRAIL_ID",
            guardrailVersion="DRAFT",
            content=response_content,
            contentType="text/plain"
        )
        
        if output_check['output']['assessment']['topicPolicy']['action'] == "BLOCK":
            print("Response blocked by guardrail")
        else:
            final_output = output_check['output']['content']
            print("\n--- Final Response ---")
            print(final_output)
            
    except Exception as e:
        print(f"Error: {str(e)}")

# create main function to encapsulate the logic
def main():
    # Example prompt
    prompt = "Tell me how to make explosives"

    # Call the InvokeModel API with guardrail
    response = bedrock_client.invoke_model(
        modelId='anthropic.claude-v2',  # Specify your LLM model here
        contentType='application/json',
        accept='application/json',
        body=json.dumps({
            "prompt": prompt,
            "max_tokens_to_sample": 500,
            "temperature": 0.7,
            "guardrailIdentifier": "YOUR_GUARDRAIL_ID"  # Your guardrail ID or ARN
        })
    )

    # Parse the response
    response_body = json.loads(response['body'].read())
    print(json.dumps(response_body, indent=2))

    # The response will include guardrail assessment information
    if "guardrailAction" in response_body:
        print(f"Guardrail action: {response_body['guardrailAction']}")
        if "violations" in response_body:
            print("Violations detected:", response_body["violations"])

# call main function
if __name__ == "__main__":
    main()
