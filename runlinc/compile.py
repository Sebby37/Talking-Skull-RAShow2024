#!/usr/bin/python3

'''What is this script?
- Basically just a way for me to test my runlinc code without having to paste it in every time
'''

TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">

  <meta Access-Control-Allow-Origin="*">
  <meta name="viewport" content="width=device-width, height=device-height, initial-scale=1.0">
  <meta http-equiv="X-UA-Compatible" content="ie=edge">
  <style>{{CSS}}</style>
</head>
<body>
  {{HTML}}
  <script>
    window.mSec = function( delay ){
        return (
            new Promise(
                (resolve) => setTimeout(
                    () => resolve( true ), 
                delay)
            )
        );
    };
    window.digitalIn = function ( pin ) {
      return 0;
    }
    window.setServo = function ( pin, duty ) {
      return 0;
    }
    window.listenButton = null;
    window.mouthServo = null;
  
    {{JS}}
    ( async function(){
      while( true ){
        {{JS_LOOP}}
        await mSec(0);
      }
    })();
  </script>
</body>
</html>"""

def main() -> None:
    html = open("index.html").read()
    style = open("style.css").read()
    js = open("script.js").read()
    js_loop = open("loop.js").read()
    
    formatted_page = TEMPLATE.replace("{{HTML}}", html).replace("{{CSS}}", style).replace("{{JS}}", js).replace("{{JS_LOOP}}", js_loop)
    open("output.html", "w+").write(formatted_page)

if __name__ == "__main__":
    main()