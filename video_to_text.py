import os
import speech_recognition as sr 
import moviepy.editor as mp
from pydub import AudioSegment
from pydub.silence import split_on_silence

def main():
    
    r = sr.Recognizer()
    path = 'converted.wav'
    print(get_large_audio_transcription(path))
    exit()

    clip = mp.VideoFileClip('Joe_Biden_Interview.mp4')
    clip.audio.write_audiofile(r'converted.wav')


    audio = sr.AudioFile("converted.wav")


    with audio as source:
      audio_file = r.record(source)

    result = r.recognize_google(audio_file)

    # exporting the result
    with open('recognized.txt', 'w') as file:
       file.write("Recognized Speech:")
       file.write("\n")
       file.write(result)
       print("ready!")


def get_large_audio_transcription(path):
    """
    Splitting the large audio file into chunks
    and apply speech recognition on each of these chunks
    """
    r = sr.Recognizer()
    # open the audio file using pydub
    sound = AudioSegment.from_wav(path)  
    # split audio sound where silence is 700 miliseconds or more and get chunks
    chunks = split_on_silence(sound,
        # experiment with this value for your target audio file
        min_silence_len = 500,
        # adjust this per requirement
        silence_thresh = sound.dBFS-14,
        # keep the silence for 1 second, adjustable as well
        keep_silence=500,
    )
    folder_name = "audio-chunks"
    # create a directory to store the audio chunks
    if not os.path.isdir(folder_name):
        os.mkdir(folder_name)
    whole_text = ""
    # process each chunk 
    for i, audio_chunk in enumerate(chunks, start=1):
        # export audio chunk and save it in
        # the `folder_name` directory.
        chunk_filename = os.path.join(folder_name, f"chunk{i}.wav")
        audio_chunk.export(chunk_filename, format="wav")
        # recognize the chunk
        with sr.AudioFile(chunk_filename) as source:
            audio_listened = r.record(source)
            # try converting it to text
            try:
                text = r.recognize_google(audio_listened)
            except sr.UnknownValueError as e:
                print("Error:", str(e))
            else:
                text = f"{text.capitalize()}. "
                print(chunk_filename, ":", text)
                whole_text += text
    # return the text for all chunks detected
    return whole_text


if __name__ == '__main__':
    main()
