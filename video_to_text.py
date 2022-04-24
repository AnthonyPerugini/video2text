import os
import speech_recognition as sr 
import moviepy.editor as mp
from pydub import AudioSegment
from pydub.silence import split_on_silence


STAGED_FILE_DIR = 'interviews/staged/'
COMPLETED_FILE_DIR = 'interviews/completed/'


def main():

    global STAGED_FILE_DIR
    global COMPLETED_FILE_DIR


    for mp4 in os.listdir(STAGED_FILE_DIR):
        filename = mp4.split('.')[0]
        print(filename)

        # check if output folder already exists, if not, create it
        if not os.path.exists(COMPLETED_FILE_DIR + filename):
            os.mkdir(COMPLETED_FILE_DIR + filename)
            print('new directory created successfully')
        else:
            print(f'{mp4} has already been parsed! skipping')
            continue

        # convert mp4 to wav
        clip = mp.VideoFileClip(STAGED_FILE_DIR + mp4)
        clip.audio.write_audiofile(COMPLETED_FILE_DIR + filename + '/converted.wav')
        print('.wav file written')

        # chunk and parse wav into text
        text = get_large_audio_transcription(COMPLETED_FILE_DIR + filename + '/converted.wav', r)

        # exporting the result
        with open(COMPLETED_FILE_DIR + filename + '/recognized.txt', 'w') as file:
           file.write("Recognized Speech:")
           file.write("\n")
           file.write(text)
           print(f'{mp4} processed and text file written to {COMPLETED_FILE_DIR + filename + "/recognized.txt"}')


    exit()
    # remove all files from staged directory
    for mp4 in os.scandir(os.getcwd()+'/interviews/staged'):
        os.remove(mp4)
        


def get_large_audio_transcription(path):

    """
    Splitting the large audio file into chunks
    and apply speech recognition on each of these chunks
    """
    global COMPLETED_FILE_DIR 

    r = sr.Recognizer()

    sound = AudioSegment.from_wav(path)  
    print('chunking wav...')
    # splits audiofile into chunks on silences
    chunks = split_on_silence(sound,
        # experiment with this value for your target audio file
        min_silence_len = 1000,
        # adjust this per requirement (-16 default)
        silence_thresh = sound.dBFS-16,
        # keep the silence for 1 second, adjustable as well
        keep_silence=100
    )
    print(f'wav chunked into {len(chunks)} parts!')
    folder_name = "audio-chunks"
    # create a directory to store the audio chunks
    if not os.path.isdir(COMPLETED_FILE_DIR + folder_name):
        os.mkdir(COMPLETED_FILE_DIR + folder_name)
    whole_text = []
    # process each chunk 
    for i, audio_chunk in enumerate(chunks, start=1):
        last_question = False
        # export audio chunk and save it in
        # the `folder_name` directory.
        chunk_filename = os.path.join(COMPLETED_FILE_DIR, folder_name, f"chunk{i}.wav")
        audio_chunk.export(chunk_filename, format="wav")
        # recognize the chunk
        with sr.AudioFile(chunk_filename) as source:
            audio_listened = r.record(source)
            # try converting it to text
            try:
                text = r.recognize_google(audio_listened)
            except sr.UnknownValueError as e:
                print("Error:", str(e))
                if not last_question:
                    whole_text.append('\n(?)\n')
                    last_question = True
            else:
                last_question = False
                text = f"{text.capitalize()}. "
                print(f'parsing : chunk {i}/{len(chunks)} ... {text}')
                whole_text.append(text.strip())

    # return the text for all chunks detected
    return ' '.join(whole_text)


if __name__ == '__main__':
    main()
