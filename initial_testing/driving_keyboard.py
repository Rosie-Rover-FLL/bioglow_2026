from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor, ColorSensor, UltrasonicSensor, ForceSensor
from pybricks.parameters import Button, Color, Direction, Port, Side, Stop
from pybricks.robotics import DriveBase
from pybricks.tools import wait, StopWatch

hub = PrimeHub()
# pybricks blocks file:{"blocks":{"languageVersion":0,"blocks":[{"type":"blockGlobalSetup","id":"bjK,wS1MYO7aiYkFSwd{","x":171,"y":20,"deletable":false,"next":{"block":{"type":"variables_set_motor","id":"(yb{*PXMQ4AkGI%Cp+yZ","fields":{"VAR":{"id":"D2[c8TJtsF%$wFEV1puP"}},"inputs":{"PORT":{"shadow":{"type":"blockParametersPort","id":"`gDRtmO?[19f*Nc2u*Y*","fields":{"NAME":"D"}}},"POSITIVE_DIRECTION":{"shadow":{"type":"blockParametersDirection","id":"V7I;|_x3KSh{IQc,/Tew","fields":{"SELECTION":"Direction.CLOCKWISE"}}}},"next":{"block":{"type":"variables_set_motor","id":"7c{8K*8U3Aqe9IVY$i2Q","fields":{"VAR":{"id":"fOjS9/iQg,[9%6vxC[`|"}},"inputs":{"PORT":{"shadow":{"type":"blockParametersPort","id":"M19dT%#GXg8x!;X;9!am","fields":{"NAME":"B"}}},"POSITIVE_DIRECTION":{"shadow":{"type":"blockParametersDirection","id":"q!]xl9.({V_GqVR*jb^M","fields":{"SELECTION":"Direction.COUNTERCLOCKWISE"}}}},"next":{"block":{"type":"variables_set_prime_hub","id":"HWpemtlDUK[OydJM]K_u","extraState":{"optionLevel":0},"fields":{"VAR":{"id":"`#[T%i-#s/5:LJyfnKmv"}},"next":{"block":{"type":"variables_set_drive_base","id":"dD7S@X*ahj.6RG6_henL","fields":{"VAR":{"id":"(n?RyfX;{[R5FXi=jCOa"}},"inputs":{"VAR":{"shadow":{"type":"variables_get_motor_device","id":"$NG|JG[wVUR[msW~S7+i","fields":{"VAR":{"id":"D2[c8TJtsF%$wFEV1puP","name":"left wheel","type":"Motor"}}}},"VAR2":{"shadow":{"type":"variables_get_motor_device","id":"^VR|9qyw6u$x2s}rp*pq","fields":{"VAR":{"id":"fOjS9/iQg,[9%6vxC[`|","name":"right wheel","type":"Motor"}}}},"VALUE0":{"shadow":{"type":"unit_distance","id":"$DLG8)64i6pCjYh`gR,_","fields":{"VALUE0":56}}},"VALUE1":{"shadow":{"type":"unit_distance","id":"cG89WIQ,wjdw`)qi({^8","fields":{"VALUE0":114}}}},"next":{"block":{"type":"variables_setup_any","id":"uN[7T%ug8Y86=BKqMs7e","fields":{"VAR":{"id":"(@+Z${P%%~:H6%(s[mIQ"}},"inputs":{"VALUE0":{"shadow":{"type":"blockMathNumber","id":"/grG%c*:ZOAPUhR6D_cD","fields":{"NUM":0}}}}}}}}}}}}}}},{"type":"blockGlobalStart","id":"3tJe|AWl0baN(wH9a$@.","x":111,"y":347,"deletable":false,"next":{"block":{"type":"blockPrint","id":"j,,T}?rBkaW$1v?olp4p","extraState":{"optionLevel":0},"inputs":{"TEXT0":{"shadow":{"type":"text","id":"!x5.0YiWya^`(y)yO5B8","fields":{"TEXT":"Hello, Pybricks!"}}}},"next":{"block":{"type":"blockFlowWhile","id":"3%R[?[w-q.nm/j6^4gJ-","fields":{"MODE":"WHILE"},"inputs":{"BOOL":{"shadow":{"type":"blockLogicTrue","id":"R`~EY~%01ga)T#7vUq]@"}},"DO":{"block":{"type":"blockVariableSetValue","id":"|px)bM(;.d)Fy~M[9j`j","inputs":{"VAR":{"shadow":{"type":"variables_get_any","id":"u@OW/y0YDe_YV9KdkT4^","fields":{"VAR":{"id":"(@+Z${P%%~:H6%(s[mIQ","name":"last_key","type":"Any"}}}},"VALUE0":{"shadow":{"type":"blockMathNumber","id":"q6GsD_Z0kfp8pdUG6e0O","fields":{"NUM":0}},"block":{"type":"blockReadInput","id":"EtzS8!BOO@d:ULK6.t!C","fields":{"METHOD":"READ_INPUT_LAST_CHAR"}}}},"next":{"block":{"type":"blockPrint","id":"!a)`h2r`k)!()bX,0.:8","extraState":{"optionLevel":0},"inputs":{"TEXT0":{"shadow":{"type":"text","id":"@Cjenss@dIe82wy:y+9S","fields":{"TEXT":"abc"}},"block":{"type":"blockVariableGetValue","id":"$V~Tp=r4H;^ijfFeC~,)","inputs":{"VAR":{"shadow":{"type":"variables_get_any","id":"Nt#;+ZhDgoF=?$H,xVx,","fields":{"VAR":{"id":"(@+Z${P%%~:H6%(s[mIQ","name":"last_key","type":"Any"}}}}}}}},"next":{"block":{"type":"blockIfElse","id":"pQ=*C:=K.-?.E4kp6TAz","extraState":{"optionLevel":1},"inputs":{"IF0":{"shadow":{"type":"blockLogicTrue","id":"8p~aw;3$o]FNhJXEygxj"},"block":{"type":"blockLogicCompare","id":"K_45x/2TGHI,MGBF1iiG","fields":{"OP1":"EQ"},"inputs":{"A":{"shadow":{"type":"blockMathNumber","id":",RVlW78GGBGh[T.zwk^=","fields":{"NUM":45}}},"B":{"shadow":{"type":"blockMathNumber","id":"!b)VzH{`xU|k8pqqwh*$","fields":{"NUM":4}},"block":{"type":"blockVariableGetValue","id":"QCAdknv#9igOc`Pntio!","inputs":{"VAR":{"shadow":{"type":"variables_get_any","id":"0m@*{m=]7*jFx*bor?u}","fields":{"VAR":{"id":"(@+Z${P%%~:H6%(s[mIQ","name":"last_key","type":"Any"}}}}}}}}}},"DO0":{"block":{"type":"blockPrint","id":"b.557=CV4@~1w.mowCa!","extraState":{"optionLevel":0},"inputs":{"TEXT0":{"shadow":{"type":"text","id":"R+}mPz=N7lcaxAg}@zF*","fields":{"TEXT":"Go!"}}}},"next":{"block":{"type":"blockDriveBaseMove","id":"sD1HgN0lg*Oe+%`7KaKj","extraState":{"optionLevel":1},"fields":{"METHOD":"DRIVEBASE_MOVE_STRAIGHT"},"inputs":{"VAR":{"shadow":{"type":"variables_get_drive_base_device","id":".wXM2rm(jKJBtRSQ[.c`","fields":{"VAR":{"id":"(n?RyfX;{[R5FXi=jCOa","name":"drive base","type":"DriveBase"}}}},"ARG0":{"shadow":{"type":"unit_distance","id":"G%(3vBfEgeXgZUP012Gu","fields":{"VALUE0":250}}},"THEN":{"shadow":{"type":"parameters_stop_4","id":"c=@THE|A?tJ.DJC1|N9~","fields":{"VALUE":"Stop.HOLD"}}}}}}}},"ELSE":{"block":{"type":"blockMotorStop","id":"%jFl?u0mvR2u?/@$/TIj","inputs":{"VAR":{"shadow":{"type":"variables_get_simple_motor_device","id":"rlQ7sj4Z0ECcOX#mcF[W","fields":{"VAR":{"id":"D2[c8TJtsF%$wFEV1puP","name":"left wheel","type":"Motor"}}}},"VALUE0":{"shadow":{"type":"parameters_stop_3","id":"LZD*MsBJ_JAqJfllNRW+","fields":{"VALUE":"Stop.COAST"}}}}}}},"next":{"block":{"type":"blockWaitTime","id":"P`Jl+[YiTAabcnG:brRn","inputs":{"VALUE0":{"shadow":{"type":"unit_time","id":"vH,1@-lYq|J)1WNcG?Sy","fields":{"VALUE0":1000}}}}}}}}}}}}}}}}}},{"type":"blockLogicCompare","id":"gMOi{AtDy2t{x|V__$bS","x":573,"y":338,"enabled":false,"fields":{"OP1":"EQ"},"inputs":{"A":{"shadow":{"type":"blockMathNumber","id":"H9T+bG^)=@|ov{]O^H9(","fields":{"NUM":3}},"block":{"type":"blockVariableGetValue","id":"u$n0MOFzw,/[6e?aQGsW","inputs":{"VAR":{"shadow":{"type":"variables_get_any","id":"gFr?38eZ#*2(;FqL(WY|","fields":{"VAR":{"id":"(@+Z${P%%~:H6%(s[mIQ","name":"last_key","type":"Any"}}}}}}},"B":{"shadow":{"type":"blockMathNumber","id":"-:MOXk_dHWOg-BOJJR+*","fields":{"NUM":1}}}}}]},"variables":[{"name":"red","id":"DFP[t[3`!FV);FSyMA*!","type":"ColorDef"},{"name":"orange","id":"jKHDI/MxNN5dgEx9b:;B","type":"ColorDef"},{"name":"yellow","id":"qH_NNbr#5-]dfkS*C)9}","type":"ColorDef"},{"name":"green","id":"jQl?%:E8F*ft?2RJs6Q5","type":"ColorDef"},{"name":"cyan","id":"[uOdcF]o+^/AAX#D4sRK","type":"ColorDef"},{"name":"blue","id":"DSntlAXLXgKJMdX6sg`v","type":"ColorDef"},{"name":"violet","id":"e/z5DvlYd8w3qd331M4?","type":"ColorDef"},{"name":"magenta","id":"G3WUk9`z;b~u;Y-w:!o(","type":"ColorDef"},{"name":"white","id":"Fk7H7JeBo89y:8HrD:x`","type":"ColorDef"},{"name":"none","id":"8_T=bQ6m^;[,JDFc.;^|","type":"ColorDef"},{"name":"prime hub","id":"`#[T%i-#s/5:LJyfnKmv","type":"PrimeHub"},{"name":"drive base","id":"(n?RyfX;{[R5FXi=jCOa","type":"DriveBase"},{"name":"left wheel","id":"D2[c8TJtsF%$wFEV1puP","type":"Motor"},{"name":"right wheel","id":"fOjS9/iQg,[9%6vxC[`|","type":"Motor"},{"name":"","id":"t!8*=/K3ymPuR(h{6Hr6","type":"Any"},{"name":"last_key","id":"(@+Z${P%%~:H6%(s[mIQ","type":"Any"},{"name":"data","id":"NySE#K@e0)gcoiMQr]-u","type":"Any"}],"info":{"type":"pybricks","version":"2.0.0"},"workspaceOptions":{"scrollX":83.428562326536,"scrollY":33.36080666521406,"scale":0.5112054750305813}}
from pybricks.hubs import PrimeHub
from pybricks.parameters import Direction, Port
from pybricks.pupdevices import Motor
from pybricks.robotics import DriveBase
from pybricks.tools import read_input_byte, wait

# Set up.
left_wheel = Motor(Port.D, Direction.COUNTERCLOCKWISE)
right_wheel = Motor(Port.B, Direction.CLOCKWISE)
prime_hub = PrimeHub()
drive_base = DriveBase(left_wheel, right_wheel, 56, 114)
last_key = 0


# The main program starts here.
print('Hello, Pybricks!')
while True:
    # Read the text string of the key pressed
    last_key = read_input_byte(True, True)
    
    if 'w' == last_key:
        # print("Forward")
        drive_base.drive(200, 0)      # Drive forward smoothly
    elif 's' == last_key:
        drive_base.drive(-200, 0)     # Drive backward smoothly
        # print("Back")
    elif 'a' == last_key:
        drive_base.drive(0, -50)      # Turn left smoothly
        # print("Left")
    elif 'd' == last_key:
        drive_base.drive(0, 50)       # Turn right smoothly
        # print("Right")
    else:
        drive_base.stop()             # Stop instantly when no key is pressed
        # print("stop")
        
    wait(100)                          # Fast check for responsive steering

