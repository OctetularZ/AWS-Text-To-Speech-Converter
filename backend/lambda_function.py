import json
import boto3
import uuid

polly = boto3.client('polly')
s3 = boto3.client('s3')

BUCKET_NAME = 'zenshittsbucket'

CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'POST, OPTIONS'
}

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        text = body.get('text')
        voice = body.get('voice', 'Joanna')

        if not text:
            return {
                'statusCode': 400,
                'headers': CORS_HEADERS,
                'body': json.dumps({'error': 'Text is required.'})
            }

        response = polly.synthesize_speech(
            Text=text,
            VoiceId=voice,
            OutputFormat='mp3'
        )

        audio_stream = response.get('AudioStream')

        if audio_stream:
            file_name = f"{uuid.uuid4()}.mp3"
            s3.put_object(
                Bucket=BUCKET_NAME,
                Key=file_name,
                Body=audio_stream.read(),
                ContentType='audio/mpeg',
                ACL='public-read'
            )

            audio_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{file_name}"

            return {
                'statusCode': 200,
                'headers': CORS_HEADERS,
                'body': json.dumps({'audioUrl': audio_url})
            }

        return {
            'statusCode': 500,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': 'Failed to synthesize speech'})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': str(e)})
        }
