import grpc
import service_pb2
import service_pb2_grpc

def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = service_pb2_grpc.VideoServiceStub(channel)
        response = stub.ServerActive(service_pb2.Empty())
        print("Server active response: ", response)

        # Example for Upload call
        with open('video.mp4', 'rb') as video_file, open('audio.mp3', 'rb') as audio_file:
            upload_response = stub.Upload(
                service_pb2.UploadRequest(
                    video=video_file.read(),
                    audio=audio_file.read()
                )
            )
            print("Upload response: ", upload_response)

if __name__ == '__main__':
    run()
