function decodeUplink(input) {
      var event = ''; 
    let lenght = input.bytes.length;
    var idx = 0 ;
    var code = 0 ;
    while ( idx < lenght ) 
    {
      code = input.bytes[idx]
      if (code == 01 ) {
        event = String.fromCharCode(input.bytes[idx+1]); 
        idx +=1 ;
      }
      if (code == 02 ) {
        temp  = input.bytes[idx+1] + (input.bytes[idx+2] * 256);
        temp = Math.round(temp/10)
        idx +=2 ;
      }
      if (code == 03 ) {
        default_code = input.bytes[idx+1]; 
        idx +=1 ;
      }
      idx +=1;
    }
    return {
      data: {event: event, temp: temp, default :default_code},
      warnings: [],
      errors: []
    };
  }
    