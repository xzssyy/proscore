import requests
import base64
import json

import time


def get_pronScore(audioFile, referenceText):
    subscriptionKey = "8ffaa1d1913045698c564e3d126d518e"  # replace this with your subscription key
    region = "eastus"  # replace this with the region corresponding to your subscription key, e.g. westus, eastasia

    # a common wave header, with zero audio length
    # since stream data doesn't contain header, but the API requires header to fetch format information, so you need post this header as first chunk for each query
    def get_chunk(audio_source, chunk_size=1024):
        while True:
            # time.sleep(chunk_size / 32000) # to simulate human speaking rate
            chunk = audio_source.read(chunk_size)
            if not chunk:
                # global uploadFinishTime
                # uploadFinishTime = time.time()
                break
            yield chunk

    # build pronunciation assessment parameters
    # referenceText = 'funny'
    pronAssessmentParamsJson = "{\"ReferenceText\":\"%s\",\"GradingSystem\":\"HundredMark\",\"Dimension\":\"Comprehensive\",\"EnableMiscue\":\"True\"}" % referenceText
    pronAssessmentParamsBase64 = base64.b64encode(bytes(pronAssessmentParamsJson, 'utf-8'))
    pronAssessmentParams = str(pronAssessmentParamsBase64, "utf-8")
    language = 'en-US'

    # build request
    url = "https://%s.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1?language=%s&usePipelineVersion=0" % (
        region, language)
    headers = {'Accept': 'application/json;text/xml',
               'Connection': 'Keep-Alive',
               'Content-Type': 'audio/wav; codecs=audio/pcm; samplerate=44100',
               'Ocp-Apim-Subscription-Key': subscriptionKey,
               'Pronunciation-Assessment': pronAssessmentParams,
               'Transfer-Encoding': 'chunked',
               'Expect': '100-continue'}

    # audioFile = open('audio.wav', 'rb')
    # audioFile = open('../bad.wav', 'rb')
    # send request with chunked data
    response = requests.post(url=url, data=get_chunk(audioFile), headers=headers)
    # getResponseTime = time.time()
    audioFile.close()

    # latency = getResponseTime - uploadFinishTime
    # print("Latency = %sms" % int(latency * 1000))


    return response.json()