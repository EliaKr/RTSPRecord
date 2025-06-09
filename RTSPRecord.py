from datetime import datetime
import json
import time
import subprocess
import os
import multiprocessing

class Config:
    def __init__(self):
        pass
    
class StreamList:
    def __init__(self):
        self.streamList = self.loadStreamList()
    
    def loadStreamList(self):
        streamList = []
        with open("streamlist.json", "r") as streamListFile:
            streamImportList = json.load(streamListFile)
            print(streamImportList)
            for streamListDictionary in streamImportList:
                for streamNameKey in streamListDictionary.keys():
                    streamObject = self.createStreamObject(streamNameKey, streamListDictionary)
                    streamList.append(streamObject)
        return streamList

    def createStreamObject(self, streamNameKey, streamListDictionary):
        tempStreamObject = Stream()
        tempStreamObject.setInfo(streamNameKey, streamListDictionary[streamNameKey]['address'], streamListDictionary[streamNameKey]['port'], streamListDictionary[streamNameKey]['username'], streamListDictionary[streamNameKey]['password'], streamListDictionary[streamNameKey]['streamPath'], streamListDictionary[streamNameKey]['recordPath'], streamListDictionary[streamNameKey]['recordingSegmentDuration'])
        return tempStreamObject

    def getStreamList(self):
        return self.streamList

class Stream:
    def __init__(self):
        pass
    
    def setInfo(self, streamName, streamAddress, streamPort, streamUsername, streamPassword, streamPath, recordPath, recordingSegmentDuration):
        self.streamName = streamName
        self.streamAddress = streamAddress
        self.streamPort = streamPort
        self.streamUsername = streamUsername
        self.streamPassword = streamPassword
        self.streamPath = streamPath
        self.recordPath = StorageLocation(recordPath, streamName)
        self.recordingSegmentDuration = recordingSegmentDuration
        self.rtspUrl = self.createRtspUrl()

    def createRtspUrl(self):
        rtspUrl = "rtsp://" + self.streamUsername + ":" + self.streamPassword + "@" + self.streamAddress + ":" + self.streamPort + self.streamPath
        return rtspUrl
    
class Recording:
    def __init__(self):
        pass
    
    def recordAllStreams(self, streamListObject):
        for i in streamListObject.streamList:
            self.startRecordingProcess(i)

    def startRecordingProcess(self, streamObject):
        newProcess = multiprocessing.Process(target=self.startLoopedRecording, args=(streamObject,))
        newProcess.start()
        print(f"Started process for {streamObject.streamName} with ID: {newProcess.pid}")

    def startLoopedRecording(self, streamObject):
        while True:
            while streamObject.recordPath.getDirectorySize() < streamObject.recordPath.maxSize:
                current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                recording_filename = f"{streamObject.recordPath.directoryPath}/{current_time}.mp4"
                # recording_path = streamObject.recordPath.directoryPath + "/" + recording_filename

                ffmpeg_process = subprocess.Popen(f"ffmpeg -rtsp_transport tcp -i {streamObject.rtspUrl} -t {streamObject.recordingSegmentDuration} -c:v copy -c:a aac -b:a 128k -movflags +faststart -f mp4 {recording_filename}", shell=True)
                # For lower resource usage copy the audio stream. You can also use this command to lower memory usage:
                # ffmpeg_process = subprocess.Popen(f"ffmpeg -rtsp_transport tcp -fflags nobuffer -i {streamObject.rtspUrl} -t {streamObject.recordingSegmentDuration} -c:v copy -an -movflags +faststart -f mp4 {recording_filename}", shell=True)
                time.sleep(int(streamObject.recordingSegmentDuration))
                ffmpeg_process.terminate()
            else:
                streamObject.recordPath.deleteOldestFile()
            
class StorageLocation:
    def __init__(self, generalDirectory, streamName):
        self.generalDirectory = generalDirectory
        self.createDirectory(streamName)
        self.setMaxSize()

    def getDirectorySize(self):
        directorySize = 0
        for dirpath, dirnames, filenames in os.walk(self.directoryPath):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                directorySize += os.path.getsize(fp)
        return directorySize / 1000000000

    def createDirectory(self, streamName):
        self.directoryPath = os.path.join(self.generalDirectory, streamName)
        if not os.path.exists(self.directoryPath):
            os.makedirs(self.directoryPath)


    def setMaxSize(self):
        with open('config.txt', 'r') as file:
            for line in file:
                if line.startswith('directoryMaxSize'):
                    max_size = line.split('=')[1].strip()
                    try:
                        self.maxSize = int(max_size)
                    except ValueError:
                        print("Invalid value for directoryMaxSize in the config file.")
                    break
    
    def deleteOldestFile(self):
        files = os.listdir(self.directoryPath)
        oldest_file = min(files, key=lambda f: datetime.strptime(f.split(".")[0], "%Y-%m-%d_%H-%M-%S"))
        file_path = os.path.join(self.directoryPath, oldest_file)
        os.remove(file_path)

class Main:
    def __init__(self):
        self.setup()
        self.run()

    def setup(self):
        self.streamList = StreamList()
    
    def run(self):
        recordObject = Recording()
        recordObject.recordAllStreams(self.streamList)

        while True:
            pass

run = Main()
