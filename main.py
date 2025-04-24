import boto3, os, argparse, sys, datetime, socket
from dotenv import load_dotenv

class Bucket:

    def __init__(self, url: str, access_key: str, secret_key: str, bucket_name: str):
        self.__url: str = url
        self.__access_key: str = access_key
        self.__secret_key: str = secret_key
        self.__bucket_name: str = bucket_name
        self.s3 = self.__connect()

    def __connect(self):
        try:
            return boto3.resource(
                's3',
                endpoint_url=self.__url,
                aws_access_key_id=self.__access_key,
                aws_secret_access_key=self.__secret_key
            )
        except Exception as e:
            raise Exception(f"Error connecting to resource: {e}")
    
    def get_bucket(self, bucket_name: str):
        try:
            bucket = self.s3.Bucket(bucket_name)
            if bucket.creation_date:
                return bucket
            else:
                raise Exception(f"Bucket '{bucket_name}' does not exist or is not accessible.")
        except Exception as e:
            raise Exception(f"Error accessing bucket '{bucket_name}': {e}")

    def build_object_name(self, file_path: str, object_name: str = '') -> str:
        if not object_name:
            object_name = os.path.basename(file_path)

        now = datetime.datetime.now().strftime('%Y-%m-%d')
        hostname = socket.gethostname()

        return f"{now}/{hostname}/{object_name}"

    def ls(self, directory: str = '') -> list:
        try:
            bucket = self.get_bucket(self.__bucket_name)
            if directory:
                prefix = directory if not directory or directory.endswith('/') else directory + '/'
                return [obj.key for obj in bucket.objects.filter(Prefix=prefix)]
            else:
                return [obj.key for obj in bucket.objects.all()]
        except Exception as e:
            raise Exception(f"Error listing objects in bucket '{self.__bucket_name}': {e}")

    def upload_file(self, file_path: str, object_name: str = '') -> None:
        try:
            bucket = self.get_bucket(self.__bucket_name)
            final_object_name = self.build_object_name(file_path, object_name)
            bucket.upload_file(file_path, final_object_name)
        except Exception as e:
            raise Exception(f"Error uploading file '{file_path}' to bucket '{self.__bucket_name}': {e}")

    def download_file(self, file_name: str, destination: str = '') -> None:
        try:
            bucket = self.get_bucket(self.__bucket_name)

            if not destination:
                destination = os.path.join(os.getcwd(), os.path.basename(file_name))
            elif os.path.isdir(destination):
                destination = os.path.join(destination, os.path.basename(file_name))
                
            os.makedirs(os.path.dirname(destination), exist_ok=True)
            bucket.download_file(file_name, destination)
            print(f"Downloaded '{file_name}' to '{destination}'")
        except Exception as e:
            raise Exception(f"Error downloading file '{file_name}' from bucket '{self.__bucket_name}': {e}")

    def delete_file(self, file_name: str) -> None:
        try:
            bucket = self.get_bucket(self.__bucket_name)
            bucket.delete_objects(Delete={'Objects': [{'Key': file_name}]})
            print(f"Deleted '{file_name}' from bucket '{self.__bucket_name}'")
        except Exception as e:
            raise Exception(f"Error deleting file '{file_name}' from bucket '{self.__bucket_name}': {e}")

if __name__ == "__main__":

    def load_env_variables() -> dict:
        load_dotenv()
        return {
            'ACCESS_KEY': os.getenv('ACCESS_KEY'),
            'SECRET_KEY': os.getenv('SECRET_KEY'),
            'BUCKET_NAME': os.getenv('BUCKET_NAME'),
            'URL': os.getenv('URL')
        }

    # Load environment variables from .env file
    env_params = load_env_variables()

    # Main parser
    parser = argparse.ArgumentParser(description='Interact with an S3 bucket.')

    # Common S3 connection arguments (can be overridden by CLI)
    parser.add_argument('--bucket_name', type=str, default=env_params.get('BUCKET_NAME'), help='Name of the S3 bucket')
    parser.add_argument('--access_key', type=str, default=env_params.get('ACCESS_KEY'), help='S3 access key')
    parser.add_argument('--secret_key', type=str, default=env_params.get('SECRET_KEY'), help='S3 secret key')
    parser.add_argument('--url', type=str, default=env_params.get('URL'), help='S3 URL endpoint')

    # Subparsers for actions
    subparsers = parser.add_subparsers(dest='action', help='Action to perform', required=True)

    # Upload subparser
    parser_upload = subparsers.add_parser('upload', help='Upload a file to S3')
    parser_upload.add_argument('--file_path', type=str, required=True, help='Local path to the file to upload.')
    parser_upload.add_argument('--object_name', type=str, help='Optional S3 object name (defaults to date/hostname/filename).')

    # List subparser
    parser_ls = subparsers.add_parser('ls', help='List objects in S3 bucket/directory')
    parser_ls.add_argument('--directory', type=str, default='', help='Optional directory prefix to list.')

    # Download subparser
    parser_download = subparsers.add_parser('download', help='Download a file from S3')
    parser_download.add_argument('--file_name', type=str, required=True, help='S3 object key to download.')
    parser_download.add_argument('--local_path', type=str, help='Local destination path for download. Defaults to current directory.')

    # Delete subparser
    parser_delete = subparsers.add_parser('delete', help='Delete a file from S3')
    parser_delete.add_argument('--file_name', type=str, required=True, help='S3 object key to delete.')

    # Parse arguments
    args = parser.parse_args()

    # Consolidate S3 connection parameters
    s3_params = {
        'ACCESS_KEY': args.access_key,
        'SECRET_KEY': args.secret_key,
        'BUCKET_NAME': args.bucket_name,
        'URL': args.url,
    }

    # Check if all required S3 connection parameters are present
    missing_s3_params = [key for key, var in s3_params.items() if var is None]
    if missing_s3_params:
        print(f"Error: Missing required S3 connection parameters: {', '.join(missing_s3_params)}")
        print("Please provide them via command line arguments or a .env file.")
        sys.exit(1)

    # Save parameters to .env if it didn't exist and all were provided via CLI
    cli_provided_s3_params = any([
        args.bucket_name != env_params.get('BUCKET_NAME'),
        args.access_key != env_params.get('ACCESS_KEY'),
        args.secret_key != env_params.get('SECRET_KEY'),
        args.url != env_params.get('URL')
    ])

    if not os.path.exists('.env') and cli_provided_s3_params:
        print("Saving provided S3 parameters to .env file for future use.")
        with open('.env', 'w') as f:
            if s3_params['ACCESS_KEY']: f.write(f"ACCESS_KEY={s3_params['ACCESS_KEY']}\n")
            if s3_params['SECRET_KEY']: f.write(f"SECRET_KEY={s3_params['SECRET_KEY']}\n")
            if s3_params['BUCKET_NAME']: f.write(f"BUCKET_NAME={s3_params['BUCKET_NAME']}\n")
            if s3_params['URL']: f.write(f"URL={s3_params['URL']}\n")

    #### START S3 CONNECTION AND ACTION ####
    try:
        print(f"Connecting to S3 bucket: {s3_params['BUCKET_NAME']}")
        s3_instance = Bucket(
            url=s3_params['URL'],
            access_key=s3_params['ACCESS_KEY'],
            secret_key=s3_params['SECRET_KEY'],
            bucket_name=s3_params['BUCKET_NAME']
        )

        # Execute action based on subparser choice
        if args.action == 'upload':
            s3_instance.upload_file(args.file_path, args.object_name or '')
            final_object_name = s3_instance.build_object_name(args.file_path, args.object_name or '')
            print(f"File '{args.file_path}' uploaded successfully as '{final_object_name}' to bucket '{s3_params['BUCKET_NAME']}'.")

        elif args.action == 'ls':
            print(f"Listing objects in bucket '{s3_params['BUCKET_NAME']}' (prefix: '{args.directory or "/"}'):")
            files = s3_instance.ls(args.directory)
            if files:
                for f in files:
                    print(f"- {f}")
            else:
                print("No objects found.")

        elif args.action == 'download':
            print(f"Attempting to download '{args.file_name}' from bucket '{s3_params['BUCKET_NAME']}' to '{args.local_path}'...")
            s3_instance.download_file(args.file_name, args.local_path)

        elif args.action == 'delete':
            print(f"Attempting to delete '{args.file_name}' from bucket '{s3_params['BUCKET_NAME']}'...")
            s3_instance.delete_file(args.file_name)
            print(f"File '{args.file_name}' deleted successfully from bucket '{s3_params['BUCKET_NAME']}'.")

    except Exception as e:
        print(f"Error during action '{args.action}': {e}")
        sys.exit(1)