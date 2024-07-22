from django.shortcuts import render, HttpResponse,redirect
from django.views import View
from django.conf import settings
from deepgram import DeepgramClient, SpeakOptions,PrerecordedOptions, FileSource
import os,pyaudio,requests,time,threading,wave,json
from django.http import JsonResponse
import openai




class Text_To_Speech(View):

    def get(self, request):
        return self.convert_to_speech(request)
    
    def convert_to_speech(self, request):
        with open("output.txt",'r') as file:
            ans=file.read()
            try:
                # Initialize Deepgram client with API key from settings
                deepgram = DeepgramClient(settings.DEEPGRAM_API_KEY)

                # Text to convert to speech
                text = {
                    "text": ans
                }

                # File path for saving the audio
                file_path = 'output.mp3'

                # Define SpeakOptions
                options = SpeakOptions(
                    model="aura-asteria-en",  # Adjust model if needed
                )

                # Perform text-to-speech conversion
                response = deepgram.speak.v("1").save(file_path, text, options)
                
                # Print and log the response for debugging
                print(response.to_json(indent=4))
                
                return render(request, 'index.html', {'audio_url': "D:/SDK_Assignment/output.mp3" })
            
            except Exception as e:
                # Handle exceptions and return error message
                print(f"Exception: {e}")
                return HttpResponse(f"Error: {str(e)}", content_type='text/plain')
     


class Record_Audio(View):
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    RECORD_SECONDS = 20

    def get(self, request, *args, **kwargs):
        self.start_recording()
        return HttpResponse("Recording started...")

    def start_recording(self):
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=self.FORMAT,
                                  channels=self.CHANNELS,
                                  rate=self.RATE,
                                  input=True,
                                  frames_per_buffer=self.CHUNK)
        self.filename = "input.wav"
        self.wf = wave.open(self.filename, 'wb')
        self.wf.setnchannels(self.CHANNELS)
        self.wf.setsampwidth(self.p.get_sample_size(self.FORMAT))
        self.wf.setframerate(self.RATE)
        self.frames = []

        self.recording = True

        # Start recording in a separate thread
        self.record_thread = threading.Thread(target=self.record)
        self.record_thread.start()

        # Start a timer to stop recording after RECORD_SECONDS
        self.timer_thread = threading.Thread(target=self.stop_after_delay)
        self.timer_thread.start()
        

    def record(self):
        while self.recording:
            data = self.stream.read(self.CHUNK)
            self.frames.append(data)
            self.wf.writeframes(data)

    def stop_after_delay(self):
        time.sleep(self.RECORD_SECONDS)
        self.stop_recording()

    def stop_recording(self):
        if self.recording:
            self.recording = False
            self.record_thread.join()
            self.stream.stop_stream()
            self.stream.close()
            self.p.terminate()
            self.wf.close()
            print(f"Recording stopped and saved as {self.filename}")

class Convert_to_Text(View):

    AUDIO_PATH = "./input.wav"  # Local file path

    def get(self, request, *args, **kwargs):
        try:
            # Initialize Deepgram client
            deepgram = DeepgramClient(settings.DEEPGRAM_API_KEY)

            with open(self.AUDIO_PATH, "rb") as file:
                buffer_data = file.read()

            payload: FileSource = {
            "buffer": buffer_data,
            }

            options = PrerecordedOptions(
            model="nova-2",
            smart_format=True,
            )


           # Call Deepgram to transcribe the audio
            response = deepgram.listen.prerecorded.v("1").transcribe_file(payload, options)

            # Convert the response to JSON
            response_json = response.to_json()
            print(response.to_json(indent=4))
            print("hi")
            response_json=json.loads(response_json)
            transcript=response_json["results"]["channels"][0]["alternatives"][0]["transcript"] 

            with open("question.txt", 'w') as file:
             file.write(transcript)
            
            return HttpResponse("successfully converted")
            

        except Exception as e:
            return HttpResponse(f"Exception: {e}")
        
class QueryLLM(View):
    def get(self,request):
        return self.query(request)
    
    def query(self,request):
        with open("question.txt",'r') as file:
            query=file.read()
            openai.api_key=settings.OPENAI_API_KEY
            completion = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a person who should know everything."},
                    {"role": "user", "content": query}
                ]
            )
            answer=completion.choices[0].message
            with open("output.txt","w") as file:
                file.write(answer)
        
        

