import os
import speech_recognition as sr 
import moviepy.editor as mp
from pydub import AudioSegment
from pydub.silence import split_on_silence


STAGED_FILE = 'interviews/staged/'
COMPLETED_FILE = 'interviews/completed/'


def main():

    global STAGED_FILE
    global COMPLETED_FILE


    for mp4 in os.listdir(STAGED_FILE):
        filename = mp4.split('.')[0]
        print(filename)

        # check if output folder already exists, if not, create it
        if not os.path.exists(COMPLETED_FILE + filename):
            os.mkdir(COMPLETED_FILE + filename)
            print('new directory created successfully')
        else:
            print(f'{mp4} has already been parsed! skipping')
            continue

        # convert mp4 to wav
        clip = mp.VideoFileClip(STAGED_FILE + mp4)
        clip.audio.write_audiofile(COMPLETED_FILE + filename + '/converted.wav')
        print('.wav file written')

        # chunk and parse wav into text
        r = sr.Recognizer()
        text = get_large_audio_transcription(COMPLETED_FILE + filename + '/converted.wav', r)

        # exporting the result
        with open(COMPLETED_FILE + filename + '/recognized.txt', 'w') as file:
           file.write("Recognized Speech:")
           file.write("\n")
           file.write(text)
           print(f'{mp4} processed and text file written to {COMPLETED_FILE + filename + "/recognized.txt"}')


    exit()
    # remove all files from staged directory
    for mp4 in os.scandir(os.getcwd()+'/interviews/staged'):
        os.remove(mp4)
        


def get_large_audio_transcription(path, r):

    """
    Splitting the large audio file into chunks
    and apply speech recognition on each of these chunks
    """
    global COMPLETED_FILE 

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
    if not os.path.isdir(COMPLETED_FILE + folder_name):
        os.mkdir(COMPLETED_FILE + folder_name)
    whole_text = []
    # process each chunk 
    for i, audio_chunk in enumerate(chunks, start=1):
        # export audio chunk and save it in
        # the `folder_name` directory.
        chunk_filename = os.path.join(COMPLETED_FILE, folder_name, f"chunk{i}.wav")
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
                print(f'parsing : chunk {i}/{len(chunks)}...')
                text = f"{text.capitalize()}. "
                whole_text.append(text)

    # return the text for all chunks detected
    return ' '.join(whole_text)


if __name__ == '__main__':
    main()
