import utime
class LOGGER :
    """ Logger Static Class  """
    @staticmethod 
    def log(header , msg ) : 
        lt  = utime.localtime()
        nowDay  = '{:03d}'.format(lt[7])
        nowTime = '{:02d}:{:02d}:{:02d}'.format(lt[3],lt[4],lt[5])
        print('{}\t{}|{:<24} - {}'.format(nowDay,nowTime,header,msg)  ) 

