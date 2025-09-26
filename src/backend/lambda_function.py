import json
import boto3
import uuid
import os

polly = boto3.client('polly')
s3 = boto3.client('s3')

BUCKET_NAME = os.getenv("BUCKET_NAME")

# Global CORS headers
cors_headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'POST, OPTIONS'
}

def lambda_handler(event, context):
    print("Received event:", json.dumps(event))

    # Handle preflight CORS
    if event.get("httpMethod") == "OPTIONS":
        return {
            'statusCode': 200,
            'headers': cors_headers,
            'body': json.dumps({'message': 'CORS preflight successful'})
        }

    try:
        body = json.loads(event.get('body') or '{}')
        text = body.get('text')
        voice = body.get('voice', 'Joanna')

        if not text:
            return {
                'statusCode': 400,
                'headers': cors_headers,
                'body': json.dumps({'error': 'Text is required.'})
            }

        # Call Polly
        response = polly.synthesize_speech(
            Text=text,
            VoiceId=voice,
            OutputFormat='mp3'
        )

        audio_stream = response.get('AudioStream')

        if not audio_stream:
            raise Exception("No AudioStream returned from Polly")

        # Upload to S3
        file_name = f"{uuid.uuid4()}.mp3"
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=file_name,
            Body=audio_stream.read(),
            ContentType='audio/mpeg'
        )

        audio_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{file_name}"

        return {
            'statusCode': 200,
            'headers': cors_headers,
            'body': json.dumps({'audioUrl': audio_url})
        }

    except Exception as e:
        print("Error:", str(e))
        return {
            'statusCode': 500,
            'headers': cors_headers,
            'body': json.dumps({'error': str(e)})
        }
