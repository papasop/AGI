#!/usr/bin/env python3
"""
Projected-gradient response-fibre reconstruction (v0.2.2 one-click).

Starting from the frozen v1.3.1 response-matched curve, this floating-point
construction integrates the normalized Euclidean projected negative-L6
gradient

    dq/dell = -P_ker(DR3(q)) grad(L6)(q) / ||P grad(L6)||,

and applies a response-only transverse correction after every RK4 step.

The output is a candidate curve for a later validated ODE/Taylor-model proof.
It is not interval arithmetic and does not claim an exact gradient flow.
Finite-error outcomes are never used.

The frozen v0.1 model is embedded; no companion Python module is required.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import platform
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np

try:
    from scipy.optimize import least_squares
except ImportError as exc:
    raise ModuleNotFoundError(
        "scipy is required. Install it with: pip install scipy"
    ) from exc

# Frozen v0.1 source is embedded so this remains a genuine one-file Colab artifact.
_EMBEDDED_V01_B85 = (
    'c-'
    'qBXX?NR3mi^9OfkA&5(jjT=0M$`WvnAS5k0QAxIkRYVa3B(t5R(7{fU*^j|NGomRR9VLNh!&kv5!p>sO7Eqy;@NC%fGzcX6f7eD1'
    'IBpPs-'
    '*we@tStr>bi2U6AF<a+L&m6hDkMNfhVGCJmRX=;0AJl2i$lG|V<hoQ0!hbf1RGLzt|?JdNg5@AJ6VyLpT<C7Y+wCRY|om?;;RH%g'
    'Rc+Ypt}#5!0h`D2)*;d-'
    'nnXStGxS)M7MA46PC>6Wrgli$L)_oR=_v96pvhWF3eWB8=Z!#GEm^KJSRqDhbvES?2fPr)i$1bMhnE>CA~Z-'
    'VDll8)BNB3$*hn};-'
    '5gw$Ki+6POEaJ~xgq0F{(R1AYy**peWs0e1FT$w+H^G{i?r{GV2I%qPU2k}D~&!309z~2YTCdr~a0%;)SAzp)6<#UujiY}91!a0!'
    '_hYtZOb?zucSA=pyC5RWios)r*5d{!DiT`tyv6720Bkq}eLnYbfn=Ql}uA=)e1=p)*Wf5hhwQU4ZWk<c<8|D4g^z>|YapS)`zx;R'
    'q-'
    'R0F!({ul1c6D?1?(AfGb9Q;*U(Kec|B0d}mlro@7auP_Ui+uB>yxt5$@Jp%>~wlF^Pxq*Y;byh_WojaN)<m|{X9c6XyE$h>f?!M^'
    '`9TluGsw#)2r!Evzyt~*?;jK&n|9e@2}2o{?mUqJv&F4-'
    'ZWN%4dnABT7wfwcps+M*QDko273Y1b`*zM23CWII03tJ=ydianCHDskOr$2<dLnF^%hpVLR+bF&m{i@u?HDs%xvRyI#a?gkQTHTL'
    'f9xs-Tf7+Pa()2F0Y`;_<<XHwAjL8gEZO33+1;kO^Bp8$(3w7e?$?qpDf4BeR?q5wc`8BZN5!I-'
    '&dmbCP{O2jPg)Atf$v2uB8v4ISY&5^X#ek3Ojs+VvC=@WJz3nhlC!B?;Eg4{#5+Vp0na>9<4)8%mx+ERzb-Js?ToZ&l_S<T%X3zC'
    '1vq;y?G{i#T#CfT^MhY)pMMzBM74)xpYhvrXM|6=h@BqOgUE6tJ(Dj*u-'
    'q~?(FYZGv)p45@v99b}}NnQkVh#1XEHzT+QC$$B#E^@8{XoHB5wRYh!(^L7;z8$lQfb!bg<wDNLUw15h5A&7=irK;w`}h;qSd%V3'
    'PTAA^i>kCQ+hRBm55Jcou77naF3&BL&Og?W;sus(E_slC~Me3+fw%ufB5bzlEDHEahR^qDuSp%*N?z**kUgL}tt?p?#tJmcPWwWU'
    '2-'
    'EFI6b7FJ+*hCR_;*Y(U$U)rH*xYoTszxOP)H|Q0T^xscE;NK02*BEQz$m`uqFW!?sUd_(YKXb(Ev(t}ob5YKwa(3^hvx~EzKK|ri'
    'pIyBFcs{-If1aLyoYfjL%R(QnF8{&VEB*Zf*in?$skBp;zPzFmD11Ks>F=l09i>Wr`zMzmqU>55PbQuV0;m7M`-'
    'VWz&u8ZcI5Nr#r{|7;dR^QciEdA!k)L_}ldH??>ysa6C;wKpDK};IDgpmvdUE;qvnkYgGy6~o#_pkuQWEt$9R0d`6D1i%R<8&1e?'
    'R5Fp|+2VcgN@v@LpY>`=@7+j<9~+sz{QrdqnEH+12dgWafYPae6(w#?^Q;4$?Gu<`#F${-'
    ';0YSkoML;<|?6csl+L%Uj0S)iv1O#5FYChUr<=J$<a3n&TL{X4$Yu!?CM-BV+8?j%T^f#CCPp@ib4aXqk>}Sh{CunrZ73vsO`aT~'
    'pH?8~tkNK<W{`?wE#VTb`lomg72xR1;iy6UVZ=iRMl;^eQ!~jbS>rX?h+S2AA%nL8_){mT9?$r@Irwkb9iio(F#eks73+$vh(E&|'
    'KRgAxv~lo0y(l(bZgIV%by;G<!~s9LqD|<krN{OwTZ^qS-tCu>j<T$1J-'
    'V!mWEOz+NCC?bG5d1OV9>6VC)EAjdI>(4XTPHq>L=9>}nbA*62@o{J)224tHqu0aO2XL~y6oJ=MT?ov5Nw;d?M&^=eTbYn6kubE7'
    'sG7EnpEYE--!K$Wvre%=mAbo3sdPArKKZtn?nsRiy1io!()pXH^1~u5)WGKXMXa+D1!qOoqvMlHW?OB$qqivl?1beP-dln#1*CrF'
    'tPhC3`h!&N=5^h;K??tmo1SUu&akzKGnv`@8{W;#mHlcxu#iZm+3^b1G+QdK)OiUmasEf|<4YK26ay`$28$ffKXL(#q6WxYgp-'
    'T`#A|^3Gh>oGTkd+3}+e}Q*i3@$eOl=b;<#I8>_)K%+!5kc8GT{tB+-MdgAx6M*xtJ_s)TB0Gk+#R>gg!Lg#AQ#nO)e%6rf9-'
    'xbxQ+eT0%?{aHD&k?bx>M@LpiP5T*kTp_Pf%6cf58+cYhhfshi~G;9}^Zs`selBZ9gUdJ+RxPl{W$<<AGC^-'
    'ON#bz3XzI9ha^n$7k#yUyKg8A809lqsxCYO?7!eXF3w4y=so*~3!BLaAa2dpw&VNNETZ(^d5PIh1lIe~H5B7_A=*<4JP=Mb}0TC;'
    '_iJQor%bf^frvbmUa!zPYl#}Jn(#AE{(9ca%3B2Ai7f)Uw>$hrml^|+M4CVWnVaxAVUQ$xex+_fNoL+3&QaDY*G4ulV~xR78-'
    'WSa0T&9N;mBptGW)tDx<;c^Ry$pCUa2M`PK!*Hl9x!i;lZ2_$STOKDLiG*&E8SA=%;#@|iJ%JEO9Pl%j%Lp*<z!W?K1}{trQh-'
    '|kGa&<AIGpZU6EZ;(lqu{L;s>wf`8qtoY03z=V(KQi2X;72MgS09hlfwdX*~u@uvybV866k`zZ3oj{li~PC=>2xa3R5{JVF)Mf*&'
    '&(L0uke(}tM=PK1!4V&<F%p&@LI%gFWMESd(QfjGjDC=wC*rUu>XTtje25B3jhCl@fdCBY`49he-'
    '{X_(xU(3pmPbQ2PsObmz1$$*!*ngzUrixj#b;9+sbwjjx-oZvGSi1tV~E*F$V!3^H*u<juuii=Pu{L7edgSX*)2sH-'
    'ip%}(w1aSlV9H1}kgc%Kl1a}6b03LX-sasq~V2FSl7Uu#5C#Jw|iy#z);vdP4`vFV@Q61$pCU+7MJkNCDe=cIW#U(^R6aWFLb$wz'
    'A37K$62N<sdacqG}Cj1X31i*!Wg|ne&00GDZOrp`Igg`44iCdP9h|MLWS%efYKu3@O;J2tBKrbZaa#8`|Fn5oL1@AVGaOlV-'
    '+km(LxE>c1z#YPcoFNZe_k@^`&%mW8utk`iPW(emgxfB|U;thTs}wTeZtzbeMFPA5vlJPDv%ni+O9uQNx(22qKpKXS6qE+Rk#u0q'
    'g``}n3}2xHrf_Q$Xat`Cwj)-wOo;*%Knd0kh+~2Revrq2dL&*tb9%ryoInTrWX%(oOA1<pt&qwP&TN}YYC;B$%m5}17~zsa-'
    'w4nEW*bbKLQn|J6E;kN9RMSQpy0+xA}w^J7e0qTg+3-'
    'WWs06F<OK7F>Ij)x)FdeZgsh1L7bAv*kYK<TAr1r&6yid%;IHTs<Uw)5W(}kTa8;LxGFq?%swk+!WNnj2I9Q@aNrt1Nb%TMjWtqC'
    '80Yu^U6qC4&SQbjLh%z1y-'
    'mqbWl8Fn*fT8nr$)ilv0n}3pX$ct6415R1BBV^9<O$h6WCUqXOr2sR1$3iGW#Ddr3j$Eh6~IJJi}V07*R&=YcRT8vQX2>f6@)PnN'
    'B}@Q{Ko)=iHYI`(i2Fvux{I+5)Roc9N%drOctep$N~^+;89FaI%Hvxk%9?ZXL3T^qQuOi#MTn{P2>><8Xk*SOings79OPQ0>hb<S'
    'bhpQgD6CCS0EGR#fUKw72<(w={ygB@xm=oj7(o>8Bkzq=oVd1Cc=^+OXL<4B$9~pI?sH;h()O?LL?lSVVKDv9itHV1~e~X95MpKp'
    'qSwhunHLggyC<R#?q3OF##PA+$ftj$#6+a7Ud++5FE_pri8{QHA9XKw6eH_;FCaTRD?fRB3VK<4oHS&Q~FEsnS=y9BH#u8t_8UWA'
    'tBJyzy{epr6LxGZ)hC!(|89I3mt28dqQ!a0*w$7l4p$3;F~Pz;WBbz`A`VbVFWf;$cRFjDU$g@NXUCAl|=|JTp=XN_%%vmz$e1t-'
    'QICcZxJq)`yh_Pw4aAx@*|qi94Mn7l#3(|k64{e8pU~E{qI;+zEjj=Re7TT+6K}+sww}L3h^H1L7c?VJXrZOLDr}Fp74k!vRGI5&'
    'pFM4QvEc{w`t6#(Z-'
    'AIdXx1_6|+i1B}>xW{}euF$2Tea9ny4So}}4vUmdDLMLkjnLnVwen$`=lc@(jdtewF)jOWQB?5o>+Ir7wkzU(nT66`ZV3hLMoMju'
    '2{qfX5Ejd?9zelUIvzbvAMFw6TztIH@}_(a`0%)>PLjm;|d!!MgvG>^EbmH%OaX5G+yAMXd^TCfT7>_}NfS$<2m?lAJay<_*IrBb'
    '$1%BQL{4mO)GUi7I}+1+5!XnG8#QK`y@%5U_CRaT36bf3+m`ytKW`e~BnzL@0ppLE~!bsq({t2}%AuuATs<|fx;(kS%u`@8tlIuJ'
    'F}XzmB;z5gi<KF@!9{zSbP`1^m}&+qTxr8T&baDCH)OR003IF)RxtPm}$%i|~m1FNt<II58#Y`-'
    'c8K9bcF%5m2SXz}A6DqbY{JDPu=rD>8@*0q;<<#WL2>6cV<41TjrQLDP6QL~!zmS)S}=E+_;j^#!^f<U%n1tOJj9p$vbbN|feoRj'
    'rth1!Z($4a;HUvVSKq$M?}DYjNd^rj(7vKEj8kM5H%$~;W-'
    'XbG%?h*Y5n0W#qOtzGyGefx`Wl?O+n<1a%#b$!Ga^cWn(n{m8g^GpJKf<?5=`1DiuYnu1@Eae-'
    '8e}1R17V(>X3UBAd=SkK_WWYU|&3q%8;zf!UqqwVx@>YD4@vlDr)rOAxFHXlu(SJd+SwY{hRc2HcC>TROK(9W(!Q|6$i@V{0es{L'
    'Hvq?_vcYCRox|P22&|2uTu6bIw5_)Hy0@o|`4wbqsbZVb9A<sSD>SGObBLDb>&Dn_Wca_`o#gIs>ib(EWwAEpdLq(!;Fi`%+3(MN'
    ')7dT^ikUoUDe;;Io8muOxKHq|oTbae``yD5QS0ySW;WVer8D|5z{97i1RTKxShjE;w>ps813n4dnOdb;4tchyGd?5Zsl)csO21BK'
    'BO}iTi*$F=R^`X=zEtyTP-p|;2>-1)*TwdM$c=`VFVtUT6pwlji2w{n3<>)E&s}-u3+JpFBH-@%d4Q21I-'
    '1TXZ052NU4tag@@uEnbJ$_qIUq-ii5-x#nv=lC~vkn%7HWp!eq|nBMV@0eJa5ND(#}-'
    'yJS4_RLHT0|~Ppb}{o)E+jt1#p1I^3Z*5&uL4h#w$P)()}7zwv&NPzb0i{hznQWyO-XtTnmchLwF<92Ow`hV?h7RV0_BtK^Z4n$C'
    'FrLWsrvbr^_DI%{I(B78{0u;Q>zNCD|@-tclQDn)golL?gRkuY)4BDrB3%P^qT^bVu$RHbZ65Pi3a6{2NS9Ggus!G|f<GA-'
    'Q76_KC>t6{B=akLH|?go_~7fW|?=LHW<ERwSN2wt~{mdh}uZ3+G_!92N-pbZYa+jve1h-'
    'B1l*U0j4Bb;D|nFB#Wz+8d(88?Tbac<;5F=;?oNQTl&Vd?8l{@m{uO(Dqth7l91%D#8iX9;7n+OFfu0HhjK6xpm;Hp1`Clg)F#GL'
    'Ll>@4iVDZ+RDY%6G?17WJCt-BIH%XYTfBs1zlR6-g#5%2-'
    'CF2KubA0U<%3g9SBKGa%le(Co^QEpL|*Gg)ylsH!^qlBXE3uoN(hzT}Te_Ppk4|7evUi<Meb*ba?A8;-'
    '~0Vc?8u8_J8_pb}rrADjYnj)9~!QOGgx*s&x~`IVakZHUSG?y#P!RBB&^OWNJ!(<doEjJIpHW2rAwBAEb#G|G*s7W?v|YGTO2y7`'
    'VbpnMO+KWb%SzuwA)n6(J<-'
    'jwlM^gQ63zoPglOtbJX!=fPKK40i3BjG94uapb)c7dTjR9uOdq8VO{+8RkM!{WB<ey`5bC%Rs*2cyMR>h4pmCvmq1z5E-'
    'qEs@;EPi!Fe>#%5baC_w5$!5+|1gdlE+%aGrR5o91Z0k%#B%tbqsiLwBIIVpWFNB#^y$-'
    'ZtB<_Tp&bxmAZwl^iCAg_+vk4gjff|=N4pkc514u=WP|titqu_UJtJDeYiQ>{At@%C$A>Z!<*q8A6#@P2rSw!>vHp|l?O|soda-'
    '<4lKvtYdeo{o2dZN>4^j58^@%&c3t0}f&p=ECkcxxpxMem5J>kdni!G?;k5lxG>Vk}ecbE~1Jde_KY1OzptK{I-'
    'rQ27^Vxx<Fr`+S;HBy0}kXG+N$lOH7yEg8~eqQblV+DXl~p)~POwS#1jZ&CgFLQ=ogTN(6fNF4WDsv3|SbnW#lvN;^(Yj>mHicu#'
    'bSjmH~?IMmTJzmfRNzIIEVW!<nE7sJqz<3d@i8(`IASB&k636h6?t1NTbeMZC0l}j3m686fPWod&8=_;j2U=)e-'
    'O<k1HgVtDWkuv8Twuci0SbZ$HlD(-'
    'd9Vu7eMrvWj6&<NQtfuS6|GcW!^3q~846QXxp|VNAxpzL2UR=fiQv6s`VWkB3s=A<<Ax@c#@ev6T+1d(PNeK{*dfc77CHh|hkMm0'
    'h&rH9;5*APMuLF>SP==1;OLEz?{|$j(}eB6N%HM=7y?qm=!tDz{{z-gb>Ua-'
    'y+WJNRqNWDKT*eJOQ5d1r59U5XYIlNhkeuv9&$1^$GO*C>Cbn2%}3I$Y)O3Gj?xYv*-'
    'TZ&pChNv*z*>gR#xUn&Qrt?SGG8QMYg(K<6vocMFE-'
    '{!4EtyW4p@5rSEyxKH^R67h@wG;~UHitYlOcE<v)Qlx)xt@he&wHCyOR_bT4LZ*Z{G;9@WDPwHr?zp7@N*QN2=1|+uHrcB${aCb?'
    'ADvN*BX?SjQO62$P{aT)D+IcO%qc*<<uO+Laiq-GBSmll-9(f3THeCOMj>P<?p79?^6SLrPpB%;PIz1qjmqlywqoaH=N6|HL#(U-'
    'Eim5S_J2Y=5H(RtdEN45q_x($A96ku7N2)-'
    'g&u2x4%G0AFFBfD_i+<7PP+4wQD}No(Oijo)6BH|%@h4Oxwa~g4#_x@Gl^^(n0+WFVxPMVT#*5nHa7ycu6}p!upOtJA%tIwvD*xb'
    '*Ch<q?61p$iT7^&H3Q8x5CrY-xXA?~9`5$DDKacpZf#x!jm{f)z)VQ=v!P_Y&suK!K=;0HB<Ua;uc9-'
    '`nMj*$K)9q0^W(}32yXF|bJzX$VnvYxv-'
    '(rj4Qq}V7sMh`X2GOWrBj|5sS>9Cf6rSH|b5y_5lWp0jHp%YT+(&ECh?OaDAPQHDz2$e1FsNI3y@`g|l(R|&eKaMDyX9kRJGw4i='
    'x<7$>Y|-ATyff@mUi{=R#^vMDu1gJ{-'
    '!26wn7G{T_$~=CXQi*&pj#8jFz(GexS9SDvTv52`F6nt6+V<2ukjnqkmd<65S4WX_`Q^>gmlJqa%MRA4LS3XMEoL4|LdAFd?DU%<'
    '7FqPq&~39W)jXKDKq<BvLkjR?1m`^{6G}H@g_>?M`Cb+`WvUaFvCJ)vd-stiC`?jdHssrGhTC80k=En#qns%B>#Mt@}%rxE5jVKx'
    'SJ8<)Jj8#e-'
    'pWfd$3t_o1iEhEm9?`m206q<IC<7u;uk!QMzJIB0rsRc<h3Kcuol9;b9ec3P3Je62RK2%glVHh1bOnag`?s7!<5*1n#qopM+!l`b'
    'RvL$FbgD#Z~~G_C{(Wo|K28q0Kp!Jw-tir8q2KBU`g<Qwbl+ONZK*=G}-'
    'N3<!Rsy$EQMZ|_j@pgUBxa#oKHpD|e9WD1dhLkEd!E6(T3$$Kyz^c#=AeSmM?sU{`1qi8j>z-'
    '7<d=B0(QKj%LMkdLmLcywD0}D{BaYZWI1OyarUXm%QV4=-'
    'Y3p1pO=MD;VuJ6ejS)7w2`4Mf0^}+pOJ14i`{?#tW6<9eOidH}5;$0BaaQRx@#y#HDH!*Zr2T|N_ZqcQu(-'
    '~}tC)LN(^kGXf{J`#r)ev5694r=oAnx}&_SUJpOV_sKv6aTrCQL^Kgj7tkS^P-G63`xOSNXB-'
    'R@WZG)#g||i|4ED0*Uo~l0Pb8yx=WUmdqa^FYu%<+Bi~lcQ96EEImXlKZQYUlhfR`S)P$W`)WS><@P`SNvpQGzN%{&W%7Bnjrq`E'
    '6vcHy0+yp6t683)`yAsCwIQH7=BP6<cBJzRn!6%DKPL15e6ihHx&CoFqKDl1s4HvCG^_k{foj+yc0VTf<o9FtJU?v$+S2hIWOudW'
    '9MmSNadAKf7!<&T6M8iNxDXHf@IS@L=a|Hl^~-'
    'q>QB+#%W1GmA>TR5$pYX1148OzsB>AKia?XyFuj1x6wQP`@A9EY>VV!<qKHn?0G*Q%?%kQ*kem=!LWSwJRMklV=Me@;<y-'
    'yob`8c;@*EgrBadpty5ZYjSR}pR&^16Rlf3%jn@M-^jpY3c%=s7O;w%1IwUYEA8(*`nm-'
    '+N<|ev4Q!R$`XoGb^qwhwkX(SUGe8gG48k$94hBebAgAU1SnuzT_9a#7i`FdbN$|OpT5e8kG#XCGOHkicP)iAfG>WxJBK0mTKW9m'
    '-jGmI=AF&rwqRRwOZ+FHu3e4aK4R|V&AfuvSs_1Y5PahnK!gt+zmJ4+?~pKN9>%IbQ{ZFEbKZ>@?@S+#w{g@d6cgxII}ZDq}WFD$'
    'rLh<6mcSmbdMh(1SLTrz%00Zls`f|(HzC!1sFfbp?#ZffL*xL&{^Y%qv~WCI*X_{LPS1Os6_A)A$U_t%@c?CnJ{W+hQ<oCDblSH9'
    'u|n~Fpyuj_mMb2Xr8Rs30(=YXhh%{%@J$zZ44H6^umZmH~hqtVJkDwa8K7{S+%f@(xz_ItK}j5yc9m^$XlgNf(I+M%$nnd$hleuF'
    'V!pz-{0LtUAQj-i>3qx8i+?xcz`{sp-'
    '9)Tp`84niCL8Io?@&ekyZXH>NMxRTIqdv?k8&3SwA#%>}36copN&|xhl7*;0qi4G=^KP<7tN7)%J}X+Vc_nPqyjpSyC$pX(gSl(O'
    'SE^JqP5xsIO{R(;Ut0?rYyUJ1^?AJto?BD9?^YItEL75AE5Z-'
    'Myoz4jH`cyr2DI5MA?;6Vcs16KGeJmyMp<bid$Wp<Oh8lfi|rTd;n73?l&WVdif$HfnE1F<i#DaFuKq(76BWX1l8lg7vQmiE}#L4'
    '(SSt)JuM=#o`y`YoctiDj}ZgM2^8?_BZ9}s|e9Wsw^JXyh!Nuwtr5~F%+36TQ+f)d<x^CGW~F-d<vh3#ae=Lb~;oTcP#(-'
    '=ZBB9`aq%>*P4_b-z=yavTZzZerycnl1sH@k@H4bM~&-'
    'mMZV2X5<HgI$NJp~br#S*PoK{{W#tkOTYBkhV~x#=4R^)8Vu1_k)}na+vc9+`J&B0`pHdo33Fnyp>sQ+wiyWca(5cln;_(e@qNA$'
    'GvN~ULMD031&ByYnI%+po6#2YmIipuhdNr4fC02{4M)}V{WBW;s*j+`rP8%t1xpU#Gw1weFGZx?8>e^i^BQ7Gr@mHD>{BrxRatQl'
    'ZzDf2AlS-YY!O_?ZzqOh}BqOXSTiY4gUf(n@*atGB=_sbAo9Mj1MQ7P=u>j_h+TBR~dU6SR(QMgv*JRhhR$HS5fsU0GgI;NNdezw'
    'CLuVq6qm0+$s|(`!>Goz%hCJ*hb0OBln0A0>{XuhoAIh?!8w!3cC$zuyx;GRGpD7#7q!DOW;sma^%<8k(lB^0D)tcD1K3AK=N5i`'
    'lu68dnwViX^)P5A#+TSr5{-'
    'VZr<VzjB9GozIQGe~FB<^6XdF7o7*pV)EP~6I>_EUH;f$C80o^0zyot2AR!Uj7hsSnwrlsOeEOiemplxOXvm~RxI!AO1HpxpIQ%s'
    'gal)j$S~+NukG4BHnWZ=O6RY2M22Xlrr7Ce1MI8^*q1z}TAqK0J2h!>LZN_<r9gOJ%!Gnk!c=n3SQ0mANA}I}V!c)JAK9Vb@An1D'
    'm_S<cAjxxN6d66Y0g7%k6#+;bX1z_b(k@$`l|m&iEm|LHgVQU^{u=fpxXAKfG>KIH*nB@KdJ+#ue7qO-mC8f7m-'
    '@?Ch^&z}Vea3o3uuKeFuRuDJlWQ}w$sv7!6djy+{^_|e<~N)|rBCO=R_@>~I~-'
    '|rufc4OmC?wVlR;ORBv(t$i0q>0prG|HdZ`8Nk~_Asu#91(Y6;C^H~j6u6m<2BxVP*buLD^qVvvC}{I`O{wO@75igrssJwi<h?`<'
    'E}_}3Cing9yEwPSiR2QKs*w_Ptp;UdBr^ra@UiWW9qcm&yiry-Khspj#tH&p=epBg%)?}ymdAI(!=q0^wQB}V@Ch?9jUMG-'
    '4RuhzxUjIb=SgIS4$r+-d$b(*No)*;o}YRfa&{-'
    '%j=u76aVt!9PEp!3wGjr&9F1J<$=zn@p)^sONV`_S@+6krop5p@)CA|Zym<CYw&xQcSPYbs<OrP`6`Iko%3jgP0kZg9dDCuR-Oj6'
    'yHYV1&OZN?<%`DT6xERDrdkA7D=Tt}D#Kv+ynNT?j#@9DmVbGU)s-mjo{jH@@s1{5uy^S9Wnf+OwkOwj-'
    '07&>ks|H7)uEABOr^gf_vx~j!XwHV^m+=@QR8<_oFB|#WZKZwCId}bNZaLzC}|#)J!%o8^6)8}C!517yn@rtcZd|Peh>@ujkVqG_'
    'rv^^Zy%_?b!Mm(xHVMx4#w8r7|KV6%44!h;$;2YocI>6#ZlX-8bAAnzxCyqAKk{rru@=Cx;<WhT0|+$V$&+GIM9&2?!-?%NslD-'
    'MQd*>L=uO-jX$T9_OT5h)voS+)9=j_6bE#u<A2LpPIDuPytzlBgol|I(!mS=SyZrvc3CK7H*)Sfo@Y-'
    'W3f3k~_o$y$+VK6EHcTF?>af)X?}1*Bg3Krk)>Q;%+|i^7+8v)FY5I3|q0h?=`8LQHp(Hz|^@0NVY0Lkh(Fm8+BW%0eme;(QCZDr'
    '@Z5oHY7bgzr9XR!TmAwy&!jgEu%$Q&C#kP!oZBR_FhEdt^4t`O<_iOG+FM_IKUE`d~_KAc(J1Nlj2Yee6UzU>giOXkVQi`J%6;$$'
    'L?slla5+}BsQO=m_MlaZZx!H>fe}>7)%W3Mnvy16DO~rgXzuC3u)wK57k{9|sBk0+rVJ>gCjFx4h_nMUVXy59Ks<0O`9m$y4d@)z'
    '?Gy#7Isd}=j8xD&R620Y#!Xwc1z<aYA?bKeQC0?IJZ^R1cupxR{4ON1?cz00oh94di#%k9?6`gEfu)}QUG;&P0^L+11$HZ%)6!tb'
    'Wb#H7cUUS8UML9iIOK+-TXO@-^E%9wf#cR{rgM^x*C3yNHgOI^tGl1z#&yT7%ED;+)8EnOS%$Sx(BGr}-'
    '4sA%~p0<<)(JE`bqOBA{^=hz(>L|>YXzqj^p!rO1b>lA+BQgt$NVF^j6Fe5WtysE$Zc@s}uGPz>N*f)OkCDL~ifv@#m3P8a=oHZd'
    '>N_yDJERpF9FI=UFRy2(N2Myd-X&LUPDDPkP=Ic&?SHjnO!-'
    'rs%2lV7%3Z&e!#3I~{I?R)6UssCEYKYk%7J0(A*od56)MkdmhWR^`yhn>9onGT8uyJ6W2CH-PL5k`GxmUF#@~9_#hN^(e}NVY{2c'
    'P<QL0xDD)KZ|ls|WE;jB{j5h;$p_wKoxfMHJ8pt9GC=s+OKK75~v-}h;+Hlpm2SOcO5273PsLEZ0|'
)

try:
    import response_fibre_geometric_flow_preflight_v0_1 as model
    MODEL_SOURCE = "external v0.1 Python module"
except ModuleNotFoundError:
    import base64
    import types
    import zlib

    module_name = "response_fibre_geometric_flow_preflight_v0_1"
    model = types.ModuleType(module_name)
    model.__file__ = "<embedded:response_fibre_geometric_flow_preflight_v0_1.py>"
    model.__package__ = None
    embedded_source = zlib.decompress(base64.b85decode(_EMBEDDED_V01_B85))
    exec(compile(embedded_source, model.__file__, "exec"), model.__dict__)
    sys.modules[module_name] = model
    MODEL_SOURCE = "embedded frozen v0.1 module"
    print("[embedded] loaded the frozen v0.1 Hamiltonian and diagnostics")


TITLE = "RESPONSE-FIBRE PROJECTED-GRADIENT RECONSTRUCTION"
VERSION = "0.2.2-oneclick"

DEFAULT_STEPS = 80
RESPONSE_CORRECTION_GATE = 2.0e-10
MAXIMUM_CORRECTION_NORM_GATE = 2.0e-5
MINIMUM_MIDPOINT_ALIGNMENT_COSINE_GATE = 0.999
MINIMUM_STEP_L6_DECREASE_GATE = 1.0e-8
MINIMUM_PROJECTED_GRADIENT_NORM_GATE = 1.0e-5
MAXIMUM_TANGENT_RELATIVE_RESIDUAL_GATE = 5.0e-5


def banner(text: str) -> None:
    print("\n" + "=" * 120)
    print(text)
    print("=" * 120)


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def response_jacobian(point: np.ndarray) -> np.ndarray:
    return model.finite_difference_jacobian(
        model.response_feature,
        point,
        model.RESPONSE_JACOBIAN_STEP,
    )


def projected_negative_gradient(
    point: np.ndarray,
    normalize: bool = True,
) -> tuple[np.ndarray, dict[str, float]]:
    jacobian = response_jacobian(point)
    _, singular_values, vh = np.linalg.svd(jacobian, full_matrices=True)
    normal_basis = vh[: model.RESPONSE_DIMENSION, :]
    gradient = model.l6_gradient(point, model.L6_GRADIENT_STEP)
    fibre_gradient = gradient - normal_basis.T @ (normal_basis @ gradient)
    field = -fibre_gradient
    field_norm = float(np.linalg.norm(field))
    tangent_relative_residual = float(
        np.linalg.norm(jacobian @ field)
        / max(
            singular_values[0] * field_norm,
            np.finfo(float).tiny,
        )
    )
    if normalize:
        if field_norm <= np.finfo(float).tiny:
            raise ArithmeticError("projected L6 gradient vanished")
        vector = field / field_norm
    else:
        vector = field
    return vector, {
        "minimum_singular_value": float(singular_values[-1]),
        "condition_number": float(
            singular_values[0] / singular_values[-1]
        ),
        "projected_gradient_norm": field_norm,
        "tangent_relative_residual": tangent_relative_residual,
        "L6": model.l6_coefficient(point),
    }


def correct_response(
    predictor: np.ndarray,
    transverse: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
    residual = lambda correction: (
        model.response_feature(predictor + transverse @ correction)
        - model.TARGET_RESPONSE
    )
    solution = least_squares(
        residual,
        np.zeros(model.RESPONSE_DIMENSION),
        method="lm",
        jac="3-point",
        xtol=2.0e-13,
        ftol=2.0e-13,
        gtol=2.0e-13,
        max_nfev=120,
    )
    correction = np.asarray(solution.x, dtype=float)
    point = predictor + transverse @ correction

    # Explicit reduced-Newton polishing prevents a nominal LM success from
    # hiding a response residual.
    polish_steps = 0
    for _ in range(4):
        feature_residual = (
            model.response_feature(point) - model.TARGET_RESPONSE
        )
        if np.max(np.abs(feature_residual)) < 5.0e-13:
            break
        full_jacobian = response_jacobian(point)
        reduced_jacobian = full_jacobian @ transverse
        update = np.linalg.solve(reduced_jacobian, -feature_residual)
        correction += update
        point = predictor + transverse @ correction
        polish_steps += 1

    gap = float(
        np.max(
            np.abs(
                model.response_feature(point) - model.TARGET_RESPONSE
            )
        )
    )
    return point, correction, {
        "optimizer_success": bool(solution.success),
        "optimizer_nfev": int(solution.nfev),
        "polish_steps": polish_steps,
        "response_gap": gap,
        "correction_l2": float(np.linalg.norm(transverse @ correction)),
        "correction_coordinate_l2": float(np.linalg.norm(correction)),
    }


def original_curve_arclength(
    curve: model.FrozenCurve,
    quadrature_order: int = 24,
) -> float:
    nodes, weights = np.polynomial.legendre.leggauss(quadrature_order)
    total = 0.0
    for segment in range(10):
        for node, weight in zip(nodes, weights):
            scalar = 0.5 * (node + 1.0)
            total += 0.5 * weight * np.linalg.norm(
                curve.derivative(segment, float(scalar))
            )
    return float(total)


def rk4_predict(point: np.ndarray, step: float) -> np.ndarray:
    k1, _ = projected_negative_gradient(point)
    k2, _ = projected_negative_gradient(point + 0.5 * step * k1)
    k3, _ = projected_negative_gradient(point + 0.5 * step * k2)
    k4, _ = projected_negative_gradient(point + step * k3)
    return point + (step / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)


def midpoint_alignment(
    left: np.ndarray,
    right: np.ndarray,
    transverse: np.ndarray,
) -> dict[str, float]:
    midpoint, _, correction = correct_response(
        0.5 * (left + right), transverse
    )
    field, field_data = projected_negative_gradient(midpoint)
    secant = right - left
    secant_norm = float(np.linalg.norm(secant))
    cosine = float(
        np.dot(secant, field)
        / max(secant_norm * np.linalg.norm(field), np.finfo(float).tiny)
    )
    parallel_residual = float(
        math.sqrt(max(0.0, 1.0 - min(1.0, cosine * cosine)))
    )
    return {
        "midpoint_alignment_cosine": cosine,
        "midpoint_parallel_relative_residual": parallel_residual,
        "midpoint_response_gap": correction["response_gap"],
        "midpoint_correction_l2": correction["correction_l2"],
        "midpoint_projected_gradient_norm": field_data[
            "projected_gradient_norm"
        ],
        "midpoint_tangent_relative_residual": field_data[
            "tangent_relative_residual"
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--parameterization")
    parser.add_argument("--steps", type=int, default=DEFAULT_STEPS)
    parser.add_argument(
        "--arclength",
        type=float,
        help=(
            "Integration arclength. By default the script uses the arclength "
            "of the frozen v1.3.1 centre curve."
        ),
    )
    parser.add_argument(
        "--output",
        default="response_fibre_projected_gradient_v0_2_results",
    )
    parser.add_argument(
        "--allow-unfrozen-input",
        action="store_true",
    )
    args, ignored = parser.parse_known_args()
    if ignored:
        print(f"[notice] ignored notebook arguments: {ignored}")
    if args.steps < 20:
        raise ValueError("--steps must be at least 20")

    parameterization_path = model.find_parameterization(
        args.parameterization
    )
    parameterization = json.loads(
        parameterization_path.read_text(encoding="utf-8")
    )
    parameterization_hash = sha256_bytes(
        canonical_json(parameterization)
    )
    frozen_input = (
        parameterization_hash
        == model.EXPECTED_PARAMETERIZATION_SHA256
    )
    if not frozen_input and not args.allow_unfrozen_input:
        raise RuntimeError(
            "Input parameterization hash mismatch. Observed "
            f"{parameterization_hash}; expected "
            f"{model.EXPECTED_PARAMETERIZATION_SHA256}."
        )

    frozen_curve = model.FrozenCurve(parameterization)
    transverse = frozen_curve.transverse
    arclength = (
        float(args.arclength)
        if args.arclength is not None
        else original_curve_arclength(frozen_curve)
    )
    if not math.isfinite(arclength) or arclength <= 0.0:
        raise ValueError("integration arclength must be finite and positive")
    step_size = arclength / args.steps

    protocol = {
        "title": TITLE,
        "version": VERSION,
        "formal_interval_arithmetic": False,
        "purpose": (
            "construct a projected-negative-L6-gradient curve before "
            "validated ODE/Taylor-model certification"
        ),
        "model": (
            "14-segment driven qubit with common quasi-static detuning"
        ),
        "metric": model.METRIC,
        "vector_field": (
            "unit-normalized negative Euclidean projection of grad(L6) "
            "onto ker(DR3)"
        ),
        "integrator": (
            "fixed-step RK4 followed by response-only transverse correction"
        ),
        "steps": args.steps,
        "arclength": arclength,
        "step_size": step_size,
        "parameterization_sha256": parameterization_hash,
        "frozen_v1_3_1_input": frozen_input,
        "response_jacobian_step": model.RESPONSE_JACOBIAN_STEP,
        "L6_gradient_step": model.L6_GRADIENT_STEP,
        "model_source": MODEL_SOURCE,
        "gates": {
            "maximum_response_gap": RESPONSE_CORRECTION_GATE,
            "maximum_response_correction_l2": (
                MAXIMUM_CORRECTION_NORM_GATE
            ),
            "minimum_midpoint_alignment_cosine": (
                MINIMUM_MIDPOINT_ALIGNMENT_COSINE_GATE
            ),
            "minimum_step_L6_decrease": (
                MINIMUM_STEP_L6_DECREASE_GATE
            ),
            "minimum_projected_gradient_norm": (
                MINIMUM_PROJECTED_GRADIENT_NORM_GATE
            ),
            "maximum_tangent_relative_residual": (
                MAXIMUM_TANGENT_RELATIVE_RESIDUAL_GATE
            ),
        },
        "finite_error_outcomes_used": False,
        "uses_cloud_or_qpu": False,
        "uses_pasqal_credentials": False,
    }
    protocol_hash = sha256_bytes(canonical_json(protocol))

    banner(f"{TITLE} v{VERSION}")
    print("No PASQAL account, token, API key, project ID, cloud, or QPU is used.")
    print(json.dumps(protocol, indent=2))
    print(f"protocol_sha256 = {protocol_hash}")

    start_time = time.time()
    initial_predictor = frozen_curve.value(0, 0.0)
    point, _, initial_correction = correct_response(
        initial_predictor, transverse
    )
    nodes = [point.copy()]
    node_records: list[dict[str, Any]] = []
    step_records: list[dict[str, Any]] = []

    initial_field, initial_data = projected_negative_gradient(point)
    del initial_field
    node_records.append(
        {
            "node": 0,
            "arclength_parameter": 0.0,
            "response_gap": initial_correction["response_gap"],
            **initial_data,
        }
    )

    for index in range(args.steps):
        left = point
        left_l6 = model.l6_coefficient(left)
        predictor = rk4_predict(left, step_size)
        point, _, correction = correct_response(predictor, transverse)
        right_l6 = model.l6_coefficient(point)
        field, field_data = projected_negative_gradient(point)
        del field
        alignment = midpoint_alignment(left, point, transverse)
        record = {
            "step": index + 1,
            "arclength_interval": [
                index * step_size,
                (index + 1) * step_size,
            ],
            "response_gap": correction["response_gap"],
            "response_correction_l2": correction["correction_l2"],
            "L6_before": left_l6,
            "L6_after": right_l6,
            "L6_change": right_l6 - left_l6,
            **alignment,
        }
        step_records.append(record)
        nodes.append(point.copy())
        node_records.append(
            {
                "node": index + 1,
                "arclength_parameter": (index + 1) * step_size,
                "response_gap": correction["response_gap"],
                **field_data,
            }
        )
        if (
            index == 0
            or (index + 1) % max(1, args.steps // 10) == 0
            or index + 1 == args.steps
        ):
            print(
                f"[step {index + 1:04d}/{args.steps:04d}] "
                f"response={record['response_gap']:.3e} "
                f"corr={record['response_correction_l2']:.3e} "
                f"cos={record['midpoint_alignment_cosine']:.8f} "
                f"dL6={record['L6_change']:.3e}"
            )

    maximum_response_gap = max(
        item["response_gap"] for item in node_records
    )
    maximum_correction_norm = max(
        item["response_correction_l2"] for item in step_records
    )
    minimum_alignment_cosine = min(
        item["midpoint_alignment_cosine"] for item in step_records
    )
    maximum_parallel_residual = max(
        item["midpoint_parallel_relative_residual"]
        for item in step_records
    )
    maximum_l6_change = max(
        item["L6_change"] for item in step_records
    )
    minimum_l6_decrease = min(
        -item["L6_change"] for item in step_records
    )
    minimum_gradient_norm = min(
        item["projected_gradient_norm"] for item in node_records
    )
    maximum_tangent_residual = max(
        item["tangent_relative_residual"] for item in node_records
    )
    total_l6_change = (
        node_records[-1]["L6"] - node_records[0]["L6"]
    )

    gates = {
        "frozen_v1_3_1_parameterization": frozen_input,
        "complete_step_cohort": len(step_records) == args.steps,
        "all_finite": all(
            math.isfinite(float(value))
            for item in step_records
            for key, value in item.items()
            if key not in {"step", "arclength_interval"}
        ),
        "response_preserved": (
            maximum_response_gap < RESPONSE_CORRECTION_GATE
        ),
        "small_response_corrections": (
            maximum_correction_norm < MAXIMUM_CORRECTION_NORM_GATE
        ),
        "positive_gradient_alignment": (
            minimum_alignment_cosine
            > MINIMUM_MIDPOINT_ALIGNMENT_COSINE_GATE
        ),
        "every_step_strictly_decreases_L6": (
            minimum_l6_decrease > MINIMUM_STEP_L6_DECREASE_GATE
        ),
        "nonstationary_vector_field": (
            minimum_gradient_norm
            > MINIMUM_PROJECTED_GRADIENT_NORM_GATE
        ),
        "projected_field_is_tangent": (
            maximum_tangent_residual
            < MAXIMUM_TANGENT_RELATIVE_RESIDUAL_GATE
        ),
    }
    all_gates_pass = all(gates.values())
    status = (
        "PROJECTED_GRADIENT_CURVE_RECONSTRUCTION_SUPPORTED"
        if all_gates_pass
        else "PROJECTED_GRADIENT_CURVE_RECONSTRUCTION_INCONCLUSIVE"
    )
    if not frozen_input:
        status = "UNFROZEN_INPUT_DIAGNOSTIC_ONLY"

    reconstructed = {
        "title": TITLE,
        "version": VERSION,
        "protocol_sha256": protocol_hash,
        "source_parameterization_sha256": parameterization_hash,
        "metric": model.METRIC,
        "parameter": "numerical arclength ell",
        "nodes": [item.tolist() for item in nodes],
        "arclength": arclength,
        "step_size": step_size,
        "finite_error_outcomes_used": False,
    }
    reconstructed_hash = sha256_bytes(canonical_json(reconstructed))

    report = {
        "scientific_status": status,
        "all_gates_pass": all_gates_pass,
        "formal_interval_arithmetic": False,
        "validated_ODE_claimed": False,
        "exact_gradient_flow_claimed": False,
        "gates": gates,
        "protocol_sha256": protocol_hash,
        "source_parameterization_sha256": parameterization_hash,
        "reconstructed_curve_sha256": reconstructed_hash,
        "steps": args.steps,
        "arclength": arclength,
        "maximum_response_gap": maximum_response_gap,
        "maximum_response_correction_l2": maximum_correction_norm,
        "minimum_midpoint_alignment_cosine": minimum_alignment_cosine,
        "maximum_midpoint_parallel_relative_residual": (
            maximum_parallel_residual
        ),
        "maximum_step_L6_change": maximum_l6_change,
        "minimum_step_L6_decrease": minimum_l6_decrease,
        "total_L6_change": total_l6_change,
        "minimum_projected_gradient_norm": minimum_gradient_norm,
        "maximum_projected_field_tangent_relative_residual": (
            maximum_tangent_residual
        ),
        "elapsed_seconds": time.time() - start_time,
        "scope": (
            "floating-point response-corrected projected-gradient "
            "reconstruction; not a validated ODE, interval, global-fibre, "
            "holonomy, cloud, or QPU theorem"
        ),
    }

    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    (output / "protocol.json").write_text(
        json.dumps(protocol, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output / "reconstructed_curve.json").write_text(
        json.dumps(reconstructed, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output / "report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    with (output / "step_diagnostics.csv").open(
        "w", newline="", encoding="utf-8"
    ) as stream:
        flat_records = []
        for item in step_records:
            flat = dict(item)
            flat["arclength_left"] = item["arclength_interval"][0]
            flat["arclength_right"] = item["arclength_interval"][1]
            del flat["arclength_interval"]
            flat_records.append(flat)
        writer = csv.DictWriter(
            stream, fieldnames=list(flat_records[0])
        )
        writer.writeheader()
        writer.writerows(flat_records)
    (output / "provenance.json").write_text(
        json.dumps(
            {
                "python": platform.python_version(),
                "numpy": np.__version__,
                "scipy": __import__("scipy").__version__,
                "script_sha256": hashlib.sha256(
                    Path(__file__).read_bytes()
                ).hexdigest()
                if "__file__" in globals()
                else None,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    banner("FINAL RESULT")
    print(json.dumps(report, indent=2))
    print("\nInterpretation")
    if all_gates_pass:
        print(
            "  PASS: a response-corrected curve generated directly from the "
            "projected negative L6 gradient passes every declared floating-"
            "point construction gate."
        )
        print(
            "  Next: fit a validated Taylor/Chebyshev ODE atlas and prove "
            "existence, response preservation, and uniform dL6/dell < 0. "
            "This run is not itself a formal gradient-flow theorem."
        )
    else:
        print(
            "  INCONCLUSIVE: inspect the failed construction gates. Do not "
            "start the formal ODE proof until the numerical curve is stable "
            "under step halving."
        )


if __name__ == "__main__":
    main()
