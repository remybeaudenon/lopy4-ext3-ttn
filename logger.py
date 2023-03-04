import utime,os,pycom 
from machine import SD,Timer

class Persist :
    TypeFlash  =   '/flash'
    TypeSD =   '/sd'
    sd = None
    def __init__(self, persist = '/flash',  subDir = '/logs' , file = 'app-00.log' ):
        self.file = file
        self.dir = subDir
        self.persist = persist
        if ( persist == Persist.TypeSD ) :
            if (Persist.sd == None) :
                try :
                    Persist.sd = SD()
                    Persist.sd.deinit()
                    Persist.sd.init(0)
                    os.mount(Persist.sd, persist )
                except OSError :
                    print('Persist:init  <<< OSError >>> SD mount object can\'t be created on {}'.format(persist) )
                    raise OSError
                else :
                    print('Persist:init mounted on {}'.format(persist) )
            self.persist = persist
        else :
            self.persist = os.getcwd()

        # build the path
        self.path = self.persist + '/'

        if (self.dir != None ) and self.dir.startswith('/') :
            try :
                os.listdir(self.persist+ self.dir)
            except OSError :
                try :
                    print('Persist:init create new path {}'.format(self.persist+ self.dir) )
                    os.mkdir(self.persist+ self.dir)
                except OSError :
                    pass
                else:
                    self.path = self.persist + self.dir + '/'
            else:
                self.path = self.persist + self.dir + '/'
    
    def fsync(self):
        os.sync() 

    def __del__(self) :
        pass
        #Persist.sd.deinit()

class Logger(Persist) :

    __fileSize = 1 * 125   # xx  Kb
    __fileMaxNumber = 2
    __scanPeriod =  6
    __console   = True

    NVS_INDEX = "NVS_INDEX"
    __instance = None

    def __init__(self):
        super().__init__()
        self.minutes = 0
        self.ctx_log ={"fileMaxNumber":10, "console":True, "debug":False, "scanPeriod":10, "fileSize":4096},
        self.ctx_file = {"fileFormat": "app-{:02d}.log", "index":0}

        if Logger.__scanPeriod > 0 :
            self.__alarm = Timer.Alarm(self._minutes_handler, 60 , periodic=True)
        else :
            self.__alarm = None    

        Logger.__instance = self

    def _minutes_handler(self, alarm):
        self.minutes +=1
        if (self.minutes >=  Logger.__scanPeriod ) :
            self.minutes = 0
            self.checkFileSize()

    @classmethod
    def getInstance(cls) :
        if (cls.__instance == None ) :
            Logger()
        return cls.__instance

    def _loadCtxParameters(self) :
        self.ctx_log ={"fileMaxNumber":10, "console":True, "debug":False, "scanPeriod":10, "fileSize":4096},
        self.ctx_file = {"fileFormat": "app-{:02d}.log", "index":0}
        try : 
            index = pycom.nvs_get(Logger.NVS_INDEX) 
            self.ctx_file["index"] = index
        except ValueError as VE :
            pycom.nvs_set(Logger.NVS_INDEX, 0) 
            try :
                os.remove(""+self.path + self.getLogFileName() )
            except OSError as ex :
                    pass

    def checkFileSize(self) :
        fileSize = 0
        fileName = self.getLogFileName()
        try :
            stat = os.stat(""+ self.path + fileName )
            filesize = stat[6]
        except :
            self.log('Logger:checkFileSize()' ,'ERROR File {}'.format(""+ self.path + fileName))
        else :
            self.log('Logger:checkFileSize()' ,'File {}\t{} bytes'.format(""+ self.path + fileName, filesize))
            if (filesize > Logger.__fileSize * 1000  ) :
                self.__increaseFileIndex()
                idx = self.ctx_file.get('index')
                self.log('Logger:checkFileSize()','Rolling file index {} new file {}'.format(idx,self.getLogFileName() ) )
                try :
                    os.remove(""+self.path + self.getLogFileName() )
                except OSError as ex :
                    pass

    def __increaseFileIndex(self) :
        #{"index":0 ,"fileFormat":"log-trend2-{:02d}.csv"}
        idx = self.ctx_file.get('index')
        fileFormat = self.ctx_file.get('fileFormat')
        idx +=1
        if ( idx > self.__fileMaxNumber) :
            idx = 0
        self.ctx_file['index'] = idx
        pycom.nvs_set(Logger.NVS_INDEX, idx) 


    def getLogFileName(self) :
        #{"index":0 ,"fileFormat":"log-system-{:02d}.log"}
        index = self.ctx_file.get('index')
        fileFormat = self.ctx_file.get('fileFormat')
        if (index != None and fileFormat != None ) :
                return (fileFormat.format(index))
        return 'app-{}.log'.format('00')

    """ Logger Static Class  """
    @staticmethod 
    def ___log(header , msg ) : 
        lt  = utime.localtime()
        nowDay  = '{:03d}'.format(lt[7])
        nowTime = '{:02d}:{:02d}:{:02d}'.format(lt[3],lt[4],lt[5])
        print('{}\t{}|{:<24} - {}'.format(nowDay,nowTime,header,msg)  ) 

    def log(self,header,data) :

        data_string =''
        if ( type(data) == dict):
            d_string = ""
            for capteur in sorted(data.keys()) :
                d_string +=  '\t\"{}\"\t{}'.format(capteur,data[capteur])
                #ligne = json.dumps(data)
            # decimal separator add for csv with not US , UK region  
            #data_string = d_string.replace('.',',')
            data_string = d_string
        elif (type(data) == str):
            data_string = data
        elif (type(data) == int or type(data) == float ):
            data_string = type(data) + " value:" + str(data)
        else :
            data_string = 'Log:_write data can\'t be converted.. {}'.format(type(data))

        data_record = ''
        if ( type(data) == dict ) :
            data_record = '{}'.format( data_string)
        else :
            data_record = '\t\"{}\"'.format(data_string)

        lt  = utime.localtime()
        nowDay  = '{:03d}'.format(lt[7])
        nowTime = '{:02d}:{:02d}:{:02d}'.format(lt[3],lt[4],lt[5])

        header_record  =  '{} {}\t{}'.format( nowDay,nowTime,header)

        outFile = self.getLogFileName()

        line = header_record +   data_record
        if (self.__console ) : print(line)

        line += "\r\n"
        try :
            with open(""+ self.path + outFile , 'a') as l:
                l.write(line)
        except OSError :
            print("LOGGER: can't append file {}".format(self.path+outFile ) )

    def __del__(self) :
        if not self.__alarm == None : 
            self.__alarm.cancel()





