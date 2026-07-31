#!/usr/bin/env python3
"""
Validated exact-root stepwise finite-error descent (v1.3.1).

This is the formal successor of
`response_fibre_parametric_preflight_v1_1.py`.  It first reconstructs and
freezes a single global transverse gauge using response data only.  It then
uses outward-rounded Arb balls, Cauchy coefficient enclosures, analytic tail
bounds, and parameter-dependent Krawczyk operators on every scalar parameter
box.  In v1.2.2 the complete theorem-bearing Krawczyk linear algebra and
shared-endpoint comparisons are also evaluated with outward-rounded Arb
arithmetic; NumPy supplies only an arbitrary midpoint preconditioner.

A PASS first re-establishes the v1.2.2 connected local response-matched
curve, then propagates certified endpoint root boxes through a common
analytic symmetric-loss Taylor model.  It certifies strict stepwise L6
descent and strict finite-error descent on the complete declared error
window.  It does not prove pointwise monotonicity at every curve parameter,
the complete global six-dimensional fibre, a canonical metric, holonomy,
PASQAL Cloud, or QPU hardware.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import importlib
import json
import math
import platform
import subprocess
import sys
import time
import types
import zlib
from pathlib import Path
from typing import Any

import numpy as np


TITLE = "RESPONSE-FIBRE EXACT-ROOT STEPWISE DESCENT AUDIT"
VERSION = "1.3.1"
PRECISION_BITS = 192
SUBDIVISIONS = 64
CAUCHY_POINTS = 64
CAUCHY_ARCS = 64
JET_ORDER = 50
SAMPLE_RADIUS = 0.01
BOUND_RADIUS = 0.02
ROOT_RADII = (1.0e-10, 3.0e-10, 1.0e-9)
ENDPOINT_RADIUS = 3.0e-10
FIT_POINTS = 11
DEGREE = 6
LOSS_JET_ORDER = 30
LOSS_SAMPLE_RADIUS = 0.2
LOSS_BOUND_RADIUS = 0.4
FINITE_ERROR_MIN = 0.035
FINITE_ERROR_MAX = 0.13
FINITE_ERROR_BINS = 48

# Frozen v1.1.1 source, compressed so this file remains a genuine one-file
# Colab artifact.  It is executed as an in-memory module only when an external
# companion module is unavailable.
_EMBEDDED_V11_B85 = (
    "c-ozPZCl&O(&l&n3a!r<J7YU~m&`dl*Wo1047-G637Or!SROsX7N8(YjwBPvZ2tS+Ro#+WF9zmht^r%!U0qdO@7-$t_TS#_iu~<$oW70H2W|UQ-esvZ8jr`LPhlQzqB6?kAJJONqhgz-MKr&Ouk%P-Woa3wyReM2RNLm!O%mVUm5b5n;w~<<VwK0+Qp2b6j{B}->KLcDT2V$@ExZBP(SKDi1BMxtcX<>AyX|cruA?B_VNmd31o~q8^j`~2J1K$0HVIczp+({9PWv9OquD5YjEi}Q=~H02y$g#-yW1s+cKxJ<sTMtMlXw-EKq*YZT-#PeX@wT2+ND0zj4O0p<NuLAU&os$Er4p6Xk{Lz#Y2=AL_wZME2b4F0PQF(F&hAc+Pk~x`l+~!9<=MQhzqdbgei~FB`q0L0#vk{Bm=k7+xa#_lfpAiJJLQKeg3T7fczgIF4R^)C|-wUG}<<cAb5R~<>-)vL_)SJzlZsHo@cvs4SX)brzFegn`|8=Z~sRgeqa4~y2ngecJp^FE=RyB&4654M9B@HJb-O93n<wLHqCE#sh|@Jm*vrB!J;s_$+L|X1UI{KhlL8Lf0mcv8Q?Kq#b{JL%Wr{n5mn!@B6mrAU48vpWNGzz6P9<?XDn<9+BVhq5-TC5-J%x&RC9i!LEKP2ZAqf!^P}{s#v$Epw%|F)-HNXKV6n}Tr!?EdSX|k0RWBYo(-+abSjFg`ZGi-Yzv`SsVNnLfw_OMcfTW*XoE~e3+W7qV^QVtzpO5Fip8V_l7;AZc^x^p8{N$bX?)T$={h!ajAOE3!IzRsP^yIhSFUF%kj?X`zd_1F(#sdG1M}N~U?jTdzI=TsWNeKynhLPqJ8wgKSko4X~>s>-mL+~mr3M`t?Evy{mLxZr*i|7{OTLNA!T_mH_58tCaN>})_OCfT<qmd*iUqisrx(P{`AHp~ZuQ5%fHp$as^#1tQqc5iy!TaOi&X0*;w|?~N$wlz#<H^~@XFN8H`uQJ6rzh`^E<mNy?2Rf$1s5MrkI#?J-Vro&p-1!O==khCcMU#*Kc`2Z`hEP-hm*6D4_`h6pHI$y`*M18PV;;@4t_hjs5@Ds4@du-JH7jO_Wp!XIQ#P9U&rTFHv`@5(Wx7poV`0gJ{rQt8;!ujU-RrolxkTT&A;ugVM2ZnH*r$JjKQw3j<Mai&g1nh%wm##hjy)_0^G%NKJg+(o9k!|)daXA<Ar#afy0%7OrvN`I?2lzrlfbD*a8!LT5c%&fBy_wxrvi#G5Yx7__rfL!sz1Y3qI)!*KFAO{^Y~)nUpPm1O{B3e>`nHHEi_$_4xc4)CQk^2lccx>2?w3dH6ILY4~@^Kk1*f&~?{adY);zzJdQ{;E!kMuJ0^8Q#TxEY1lBJ3&YY~*EDq7@qEj4ommZHZZ2HM^=;2xI-cRVzV6ci+j1S#HhfdpEyq||GwP^&o~0YE1Nb@s+6@$aVYrs5JGO5chV6Q;i4nlgU%IyKFLiIJ13G}{3*U1b%kq5y0@mKLgNm-}wq<*!Z+J`7oB{IE@qN$pfP@aJbO%tZg`s<nOGGUVU0+(hii)Ru=F)bkJ8<${p4Rp)*L3Zrsaw8j+PY-HmH4%WsfrHS1I$L#(XXc;|5tGK@%^*RzXW|C*<AV-5C#^mH3J2n>43?O<70BioEZz#^gVO{=D^kR%o*r(e8)F{+j6;d(THBI;ke+hY51OD8|HF0Hx|n!m~Z1hu){aODt)0FzGa)l8?e=0V${r9;4=|xgY&L|Cm`3sB3T~5>)^7ZFK2?erfzyb4yy>ZKrFy)z_M-609*s8fhNyzeA_Z1M$0A8#-#2NT*L?vf)?B033P|3wtymWz`L5Y7-RUD%k`Iz1)eW$VvM^q0U3|=r3vuF8DQx<HYUO+aEm$P`MwRQ#X{-6?K5YVh68EAbie^DCC-3ruBm%qj}A^d#2GAr2kt}U91G&&F=rr8mbLV;@~*jDGUDJaKmr%jaUqM$8Jozn2mnOQ@tHLMuNxMg`i5gMXM9MS1>G`ied&9);LH*<7{2egj^nsI0b~>0b3qo?U}<+bgIP%cEgK6i7z2Q&<3WmT!)3ns#u6*(+Li+;cZI}wh6UXs(T2i1w0c-s!_!S?iG?wVUSf<533F&Hbj9~AW{hb;FtAhrp@Y%BDLCUSmk=u-7R2;~&{)u@rG+jAt+*vv18N~|;18JNFlTJvB@(GG^oTj*d*Fg;U_G!f4s*sZ9ikF)3JzI<GY;&Oi<R<WL6%*{KvWz9D`!JOeP#@ZgEHw@3!4|k(g79ZdN%lN8q6110gwl+0JDJ*^9ABU!UwI<UB_m=7+?p4!?M78k0ltA0b}U9Fn-`R<O4lPmzK1qHp~s|j?ZYDu5Q>QriNjnGqc5Vmf#w(02<^mTVQluthsMOoQ1%Ea)>+(9SApsCK;Z+Bq<}_SVADdY|ux#Y(UK2E?ZzGEW-lHFa|EM1qQ(|pteiWMW0Lzq|$QH!+=eILJ38}LPHBJEFAR6WWGRhd@>TA4do=ZU~PPc=RlTV9t2;onyhms*)#|gv&HkF2)YhzVLybpkaHlkEgh?D@Nz)Qd<ZvWndIAKd4benDIiu@In!c+0U#Yy7#4W8T$(Pk#)JZRx(&Mp@t2$@Bf{RmvBA48YoHG{u=QyvJm!r}o(3xG(#+rr`6?_OG{;=BJUdV-cn1@hkeea4fV;3^F6<}dfn)=Gfr^4WSP`hD1s_U$0Ucy_AypoX8RUccVv`*NhWH<x5>gIPfKNp)o!CrVfks&#^vZ){wV5g8;Gpn8)*%1NOtGM6E)28*`{4-tVnMGUD6p7dsL&$J3C#w2uyp{~WeSkQqM^xl;7XY(x=pGNDRaf_u-Z1w0pkhgc#I<qFr?WhEJ3itJ_(a}Bm>|OY^Kkgfn^3W!B_CWF?_)pgb+~ECBzM)1>GagklFRvio$SJrjcwt^ayH)C`8y^SW0qaFqN<#LSjs4G8PqP5&q0H1#_@KU=?u$(khwb(MYHPMH5n0Em#)FJ1jG-d{1D=tH8iOnqjPnH?Rk!4Zs?)jzNkHBMcEYKr@N!(qraei69fSK=440!^~Nd#KL<+gkct#IhYo%6qeNisg~dkoG3T}=Z_VK)(hT1HxZ%Pn8T3D1n&ayONXK{-xI8XY-5?ow33e_#=xT3OB>2VWC*@MKy9)g;4@4L^Tmc1VltqGMG``3!gWIdJ;KK9nHb<hE)Y@)X`Zpbl4FIi8USsQRkdx)aCKNhs4{sHW(!Ar<UuGHVcQEKg%4PIumKQc4r6?Z{an~-3gT>`*}933Fq7~FOROj21Y!%AyR-~)Y2<iK8D~I`p#Nk9bx#->Qbo9MxJS!|C=+LBR*E{n7jzdQLrM>O;Nu6G2j&bJdIS$(qZD4pq;{8t61wd60vVekGPr8^2q+8j#sK{$$sv$;3}Ov@4FyX!1(>!lzl0arGSg=_L#%Pg_50wa2NO(;;V=<=1v>Dyp0F|$o5DAMJ22%Q)RY(l;e^bi6G^sMQ0TU$V?s>2Tnc#s^WglK2<qUD4GunmzD*G$JQ}o<tdYeA89_bd9!o5|61=u)lCgKmHVU@Dh(eKcor8v+$UxuWjwqD2Aeyu$HiZmW52%jC0s}}CE+NE);jx)1P&HUsjDob=B8WjK44Vqcr4SUJl=uSMLZ%Z$dp39>_yTuKc>}^~iWF?NzF1q}P1yuc70anp<C45H`3J!lM6bwipmH3KFk3u`HQ0}U6u!t4Y$5Ms$uL^-1px`glQ7?=C-_2<woU;Ch=cpOdM=L`jn>hPCbRy4A5V~$mf?Y{3p~!W?Ol8zYEM&b{vVWWq-)MM4j5uCGLYh1UQR@M`9>4Jf6*8ezVq)XcVCI_tE`v+SF}+Y`bNt|YaxNfX{S|ttL0+4sNCggC+BJBJ^XE@%{AjI#unB5$g=7O6`}wWJ#HtW0fbH!DPk~thtwlxAnBLRR0<U3qu_nTSAJZtKpB>i<Udy+ivxwxGp)TQgX^#@Vl@}MM2Zi*AeUb$N3A|z2|iN|5Xe()M^0B`Dc}r<#7wL3i>FiVpVU!Z5&9~KDZ~6WDg!QNN&t*;xdZZ-Dp}3vD}jI*O7klW>DC*Vo~hdZEfb!^X_(wD(k$OhM1$y*<>g&=%N1FbL30+v^sDT9X<SWbTIZR5HI*EbREp;_1ty5TI6D9B_#!}3esnR@KAvCvE<R(rAznx}{rGF^EkCP^-Itn~s%nj@JghS)XN}j4#*<1_O>F|GQQ}zF*H>9|a}%#($V5elK%|en<oP<v52%C<JT37o57+UokhX+NPr4_o99+>Zs{T~C8I<wzE`mMb8k^9>Z7hC=d6?ct69I-O6Q6j{LzwKMqE{zj_5RV}o<Omq<p7;T5P2?~(`Q){g`P_#{tJc)?VBh}ClafU2}<!lL!Pq5V{G2MNm~#Ijg(LjG&85k0!<s6)3Pni9!V5(@qM4z4YFKac<}H!fe;Y8+<-c*Af_q)pIoY=7I_pVv(^NQcoW`UO%;_oKDzjFeq5{59$LB<q9XlkxXP~MFb!_jlbc;S(;nMuMq5dZJaXmM8RWu^F6E~Xiwj_rN0<x6oeH|E8AbPKvn`({lN%i#?MH;^`S;K`TGUmR>^92E%HE1;PIj~gkKpO{Y0|9sCQgSNXuzcad!_wy$n>^H)vfbRYemTA!Az_A9BNEBK?RpI`piIBSSLa$2}nx>DnONUsQ1K#QJk!3CoJ#D;VYbl!fSP*hh+p*@I(T)0Bawox4R_F1EGmC?V;3EH&Q&TCly$@zFm?8o3PB|Ra6{a<h!Uv<U@IR&@ZB2EiQWVNH)m*z(621+2+wYUX@w?qCPhKn`r?#m@YqSP%@&*$m_K>o*L7Xgq!PiNLn#znV5YhqXG?cqwH<|Q+u4YhR?Mj^{u;1n~(_9{fKhJf_>&Gy&lUfIb`iLtmf&>;M3c|r<?FGNN=KtLu81vzR})G7`V51#FDL&uqd?PSZ>Dr3x-ZC$KcLM{~`C?W7GEXs#WA~zHpm#TrvoVSDOg&$a*3lSH$hL)!lK=bnU=uNyJ_-tzK=*2o>!PQ<|n7As0g39nfu;sYOetx?|d{<RPwUr~k0Ms&#a>3ezl&S78#+e)D7<QapB)3Z=Y$DyxvWvU2FOSnoDlMZ0JW^dF&Oa34JhtAXzk?Z`vcio?lxHlAtYgE2fplorIWuvo=0_Y_jPh|*QIZqO?3Lep^rMnEFPpBb&9%v(swjq`;V#NDThyXbKp-$q3fh+c<j3L8{LkL3ZuU|45aDn)#oBb1tq|8F{mc8m|lF!F{e<8RSMBh~LpCo#h|&%V;>hleOgvZ8n{<ZTj7{v=TNfn}oATKw1_?S4Za(HLGAlOI#<%^S^ZY56zuQX(z-R`c^|1Nnee|Mw7+kVUTAto$&&Ep+MMFMB)Am7W!<)S<1PrtR(v<AnQ^o=^QHedl;QK9?EIT_o`OPg5fJpEhqxi_dO5KpXMskJXU?q3)VE(G%))Y9-xmqMQ^bdD6(Xi_L5eE;YK&L+v`EZSHjz@ktVf2Gfc$TFi%DqQ`Jm%Ap7J48bw5DYS2gKi+U^hNUI+zP+6ozkHhlkv!Yo-ihi)bel&JT<+tH5Tvs<;aVIaiXQN_MT(}qQ)AmuUo1kG_T1&le%r-x3kSd)_5(A}VUyJzofqM*7N~v%6{jYnb864DQw&dvjE^>jamo`juwBYyqqP<qf{4%&RD`DdZiA92-+;q%c?4@J!GAFkYm%{<NWKo;DxEn*qUAU<nG+qlw&DQ4iI_(?VQ<#1Q8b}xJkvt17DT+f6w8N7U`k!SqRZF)UFctYqs0*Vui8J5<F%U@mrHKtNHvs+onX#afk~V`yo@e7A#E3D92AA8RDLv&J{dF3Q_!T*9O=#_97MFc&E(tVJ$>X>gg5v?VD4LBQcl9eB&4fVp(}mJl80#WZAQbVmj~XJYC6OcQvXZyic_NLOnqn%J#^*6%2!oqkODqF0#~<7OHQT-L&(2rr`dH_mYFzhf_|%Hw~n;yth~eOt%aPhcy7Y`2;jrKoM-U2Nw}rSR`-Rrj>($}Y5iIy*USo@U9jP?DfU&#`d3;L?m`8+X*XLWZz)TElSg9cLZ8;Qn)nzrzF$@#hC=6ACyeN~#c5o|VWKu@|Bt;MaHe0f1o2!R0{O$tmvEUg3JtELZ6z@m(8-`Rj#Qae6=T-#f%vzIyW;hZ2Mh)4ZQJnIqxHFfur~yiIYbEoAbGx2Qea6*JC~ikOqP)T`g|gTy{a{nrwZb9O_gW<(l#jq6-8m6&2Ll=whOxqr~OF8iHGB4Gj2B^JUtv+;?!lQX*e_4pPlT_P#9W3XH28RF=p&cR3|X5t~V{sLXxI&vQm`*>XyH0$JGhev*>$Chi$VYE`%d{$YS`%>f|J%jxF>bu0@N&98Q=#60%`Bo~gjgZrc2=P6)<HGOthS!q?rzc~J`Mv1oi0PaaU2fR<iw`H)tlYFn2bPr|vhs0Z=lPC6MVRFDd7;Un1{iU)bXbgKPBRCx@u?|u-%g!iqd>`w!w%)m0O)*AXi_ABJ9*LlB&_WKe~4jsbXZ8uIk(!SoUqP2>2hl+nHQ?-Wfwxo}(8c0%<#kW3@-ANFyGJg?p(E1-5Lb%&#!kM-nWXU?9QoYuz-HWwqbq-gnXiLY8kq9Hiih2dnFaen)GUV@RgTSF5CjT_VFWohrX@A)f{Ihu_ZzG_*k*w%-6;h?5TFW0pVfm`)>d#c^Dfb<0RmiMUz?a38(8|hs@IJ|IN+j^&Rj$<55=EV+(`E%4W4#EsWFguj@n>(s@#FYlNQlRn8ZG!a&?a99h|8y79m77St7v@CpsBL`5spjxpXqcER8iJrMKl2jw9}zbIMZ6>4uBzpJLWiQLbjE@4s}zlmh7%R8XBUwx$!~E>9zX)R4l#72iBXoC}KKbeW+|K#AUP*aXNi~7AWqOq7gj3WZqvvK>KH?N6n@IdN*@4lC-+ZiinH}+(CQso8E2I@1v(f8L`mx2wDUdL#uo>Q&F6D{ach2`%r1<ob_i^VJe$dWD@roUIF|P^4kj1tHerao+)BKE_Tqpf)@We%aTdeZ9m5q8ppM_5X#XStaOtyT{ZJpwOtBp)y`kl_KuWR{aTOJ{za4^z=xG*=~PCjvfDziS_>kCrnpq)Zdf|y_@6Suzljl4h@EF4Wl3~X_G9;)-b?5|7TG^5pm;#wl%2&{wH-)vBSh)9-H=g<f+)|kT*P9XtxZk|+CjgN%uOuPrYcD2)c0jZL*zi@82{<CSI@721f4yD3TUs^Uk#99dH{max0?<&Y-rU<>7AP<_~ztl9n>nKJ`T`5%h$@|?_uS*U&vu(!ugrN(9&-*xGGAr3Q?udkcD!RNde?F=v&>9pv5aHN{R3jRw7<4nhb%!FsaJMSgp^8BH^EF#S{#e{HASI=6SDDLUfQHAo4^6-Oey;z_Zpu(J;k5HvFvoBXy9G_*6|*8WvYQ)lJhL!>dl>tK?>T`IL-IX_yYKsnWOAB$IV1K5`$Azs>ngk%4_+&gyAbkj%sCUfJy?>08hbjGr*fnTj&)Cw{$}No5tA>R+2!-=Ef-*FvRlwC0^FiSDF$?mW`JB@fE$c|+#}+Jr$VtIbZqp!O!Vpl~l`?U?<g4X6gOk<{_Ve$|n4u?<%dYz)1MNI!ZeuCs?j_PNpJGT)VVwKG;4pnC(BNH*4qUVz;EnqC2`n-bG@n{T2}#O3X%H)~yOI?&*TN~O+nCAzBCMwKG{O5N*b=OSwcoqB=7FD3Y|JrD&0J^2!GV=+~iNnzb!5Zo!ns>eMLUk^s|GUy&`d#Sin6ENL7{H5AX_g^2<bWfr={r44(m%XyP!M|;CJ2G3X$Y8S2to2-sQ&StR)j@Ey!$VEiDlwvOJtZPtZ|7DW8LqJ4$F=qEov3)Rjv#~B?ZNZqJvw<<zvbIsn!e`lJKI3z^BuyT-NPX#*R6vkT?^1=b*J%iZd|E(W7kGJqd8qj`jz%p8v;K-DjA##^zbfOqb|*;mSGyi?6R{vSVNg<(sOZ4GY~aibrUyf6BQ3kPo{$wQt8xcnsyyA*BOd_0YxQ$rqS!|hemZ?GEPK5PYDzZlUaFUNVlo<k(HTRp=cANH}ho!?%=8t^~8l<-pF@_C35tD2`1lYUbV;`?%X0=(jfPoZ)Me3$-lxR2{?BkV^Re4cJr7v?vhD<Stn;A2gx~nRD-N(J4vd1K_@LEX0^P)bTF|Sh6O{mx+k$@2Zp#yM7k1e$C%YcO68r=F`qxG=f~)K8XWThtgebSBK{xRGcP>1a?7@&O2m5l+d%$@_Uv2I3hYxe;QJ18#G7h8XIpM-k<hQ2(yXVBwO<}<>>KL_bb=#Y<xxlsQpXc<Z8@E)qz%5>tuBVD@Xt=tm+{s_q86=JNw5+SD#9(LnJWt<(k%ZAvDA}R;cCoHTwtS$Nb|g#IHHT<TNOE|Ge^~gQ0}i<lu@UQ#as3=(`CpluLw)7jKJfU`l~O|jlsltv)eS<oewEyy99pOE~)I(`=Rq_^?ZND5IjG;%zApS);EU?fC><zMgZ#>+q(XY5g5QqIYjVEeQ#khT%2GOhMQiJEa64k;w7F9j;tLM2~G96ZD}~wqS8~Ng<y|rW@a5Lpfp{zEzk3?jQy~TE-bgMp~*db>Zr3PY<Ghav^&j>fnKXSiCM2BocJ*8MlOq(Pa82#(Y6Lc_;Uie$2vX>tQ`QUV7q&mtvQ}Gj?;E!5Iz9P6#t;RMd}ivDD$?<aeFIt5dK|4Vb7mG>zwgEdYZ|-L|6v`x1b*|s|RX^fNs>@-sk8W)ph}VpE2$98Ze=q9zB!UY2T}uufa#EVAJ*IL3j5YT)PAZuG*2Q*rZ#OR6Z`1Bj@d6eIEpmQ$3w%mdi|+$V|HD59ux-N-(Q?ffh&k?T!TC6Sv68MYlz`UI(FUpN!{o5#5ew8lO_2N^f;Z&SCpnnrETF{fPbl;#o+|Z8rO%HF`9kH#z2Op!e>?QI2Tr!TZ}TUfly|$Yqm5NLxnNWaaQ2ufs6gl~B`hgUq;d<(9l&igKj-%Ai23X)#t11a!pl@h#+y_c!Il{42Omv+pS(P{_rkv|Mymi+Z%Pb~C<Avoc;qS2Zwvj}RT*YZV2>f%d0t{5h@x68J?^3#UV9{77yaG_{^EE+Xv@lG9_dXzlgaHoKzKt|JYD_zJBO)>y0MtUX)5hJcul-Y9D3r87>?&)pM}8ii2aD5aTi1h8L>vCP7%9FH!+TF?*4*y_DLaRTd5GiqE}R9JlhG!+&7=FmC4?_uoQBN3M2Hp(`2CDIZ*@77H7tCPW5nXUM+juP9JahZ@O<D0M)7ei(h1fxaXb)~u=x;P0fW5cfQtJ2naOy@hrElc0y@{Wocn~a{oG|$CBaN1GW(G_xIHA}0mM<a;aI9f&DX$j<IZ`BoV#?{~$d8OL8`~Jij*?2^E#qniwO_7XW;DNaK@6{@AbN^dY;T#V}r;5uF!Ek@(@_RNHi+@T-UJ=FJ&Od}Xozz*EaC%9SeTU9mKQ$NI$>SVzc|2%58ra<i*Zxi$Gg%R}j{eT8gRM=KjVPxZ$EaHuRvtaX8F=s#p;DU;R846mV3ihEU79DV6m`|F>fLK-?R&CFQQwxb4DHy$`$f47<e#ktRM|}+Pf@l;?!UNfAQ5Og`G7J#fOuV+Uj=U6IKPJS%9MV<1W?4+e_DqJ>R<#MNQ>xl!yGig>O)<jP4Nmaxc<0rCio&~byNhq0;v?|RVjkJ9U>#T;cs9#Iu^ky$#&}i<G*cp`}!cq{svr-#?$FHM4Cmr=g*c63+TlPs$HuuV{~2^srt&0R=#6#GyaoJ-B0b|PifgI4<%onILqiN$NzbBO6Pf4?)b94@5opY8)WxUilFw>i3nZEq=+{Nw3GLA*pxW4XaQ7SOsP<sagjSM56$k|DN}Xi&A6sl5K5-I#e$!;w~;#2KFcXe>GcL!OPiDcyJn4Y?cwL+-##3lUBHbq4Dyk>x&Ha~&lV7VHg4_Gh!DSbj-a)r(s;E?2H$z-f3Ods(CIg5n(BrjgH$&@V}JIz*xBITAqUo##Trw1&B!);0CHWLePkLj?Sxbv8x3hY{PSmP%j@vZgM}6SlpFK{vFcgJ#24}HCJbP$s&+mRC_k@HUHNgmU^`F_9WE49aoOu?wzvJIO3hyz`fQcvIZ!XuXI_ED{;JF~gPStI)okxBop=*pc$~kWn|v_;VDPwL_f>Xv*P(x8RZ5@KvdexZdo}8BTDC{A-dzr5$yYCKPF9q^_Ru12T2^L*&++xn;|cH2DNd&!;W>29?+&rhx-M=8&z*l%>%7GCe>@WyO!uD?WFwO#6@o#vT|%W}aUe@*R_jDo#q?%)6{x&wc*W^vcr~o5T6fUlSD(7GNP*2GzALwtClp+)h;NW(QY^nK`hjobJ%TzE<Lh*T`sUo=^OsMbKAvA3zaMuG(AGG&8aNwz737mM1WoTwzkELV<9Ilvt!GfSr-E*wzFG(FBlZ($=k4WnYsJp1gr)8kk!-baubr=6=%M+lMgXA<a;R_5=IyEB3j|&?@q@g0wyrNtJ8#H=Ug66A5(dwEir&HW*J1anD*q6EFS(z;&Y?Yf1J5w$83*?I>C3DHbNkip_FFr(Y%2cm8AG;@#$mJEBU8>b)O(*=)O9j_p%0?aiK#JdE2LI!!7AHEeLL5^1-^C1{_v&xe;4lu^iuoo?eD!i+-KTtl3j<1xU!$~jk_$#pb1aa_3q<-#a`4EpMdAOZN)1}6{3d|@5{aA{^{UqUk#WvfT=#VQg?DLXcHg$B_|r!DfEj!X+TKJ_oNo$Ng#(zI^KB9cg2tS<Zw`R3Ie6Z-rn#fL|&Cr3ZB;QOwzbZNl_(ESNu{`4YAcTB3`gxAVn>>uTmeR*o(p}88&j^7d_~<{0V0*;?Y!TUTp616Nu%s3i5)3=n>X1$nKR}QYI4G+eQW!MACS=_?}a$^Lz@8;Od(0ALs+?6yk<}s%QR&xLE;LYSqdNf_JY#R&-QQRnz|QuP0~7=n*}9Ilb7Io=b^*U2={&PACk9j*CB^pj4i#xZ>d1JWu048F3)r{}(P?<2&f-l@5CUm&AeIH0l1~i|P+abgT)NU8{0n<rBosInAX2lyBVAk+Zablu+rG-w*7<s!s!uL9Gr~Xs7N>-b_$GDnfeodo5GuIlFUy`+6}RJgzvzhcmwTLj3IvZBV3mR{5tx=#O7?{}e|D`}(C_`L6W!)3bkQL#zML2EU2TR;Y)5dtYss5H$#;yrkGtWoR4ab)8&9-`5eW7;PVvbU_udQ55C6bhMCEUCTl{5l3F4dgtS9Ym+2P6aMQNVHadAX{|r$B3$|3wROgxD#`d2pC;%Rc=veH;lh}1nxMa%Li4u$;=VtfG83Lr`8y_K<uncZzV6?xss60VxW1eNIu`^fW(xv3I64jj+Qtlmv3xaz_cTZUA2DO>Zv"
)


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


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def ensure_flint() -> None:
    try:
        import flint  # noqa: F401
    except ImportError:
        print("[dependencies] installing python-flint==0.8.0")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-q", "python-flint==0.8.0"],
            check=True,
        )


def find_preflight(explicit: str | None) -> Path:
    candidates = []
    if explicit:
        candidates.append(Path(explicit))
    candidates.extend(
        [
            Path("response_fibre_parametric_preflight_results/parameterization.json"),
            Path("parameterization.json"),
        ]
    )
    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()
    raise FileNotFoundError(
        "v1.1.1 parameterization.json was not found. Run "
        "response_fibre_parametric_preflight_v1_1.py first, or pass "
        "--parameterization /path/to/parameterization.json."
    )


def midpoint_radius(x) -> tuple[float, float]:
    lo = float(x.lower())
    hi = float(x.upper())
    if not math.isfinite(lo) or not math.isfinite(hi):
        raise ArithmeticError("non-finite Arb enclosure")
    return 0.5 * (lo + hi), 0.5 * (hi - lo)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--parameterization")
    parser.add_argument(
        "--output", default="response_fibre_exact_root_descent_v1_3_1_results"
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Certify only the first segment; never emits the full theorem status.",
    )
    args, ignored = parser.parse_known_args()
    if ignored:
        print(f"[notice] ignored notebook arguments: {ignored}")

    ensure_flint()
    from flint import acb, arb, ctx

    ctx.prec = PRECISION_BITS

    try:
        m = importlib.import_module("response_fibre_parametric_preflight_v1_1")
        model_source = "external companion module"
    except ModuleNotFoundError:
        module_name = "response_fibre_parametric_preflight_v1_1"
        m = types.ModuleType(module_name)
        m.__file__ = "<embedded:response_fibre_parametric_preflight_v1_1.py>"
        m.__package__ = None
        source = zlib.decompress(base64.b85decode(_EMBEDDED_V11_B85))
        exec(compile(source, m.__file__, "exec"), m.__dict__)
        sys.modules[module_name] = m
        model_source = "embedded frozen v1.1.1 module"
        print("[embedded] loaded the frozen v1.1.1 model and solver")

    try:
        preflight_path = find_preflight(args.parameterization)
    except FileNotFoundError:
        if args.parameterization:
            raise
        print(
            "[preflight] parameterization.json is absent; running the embedded "
            "complete v1.1.1 preflight first"
        )
        saved_argv = sys.argv[:]
        try:
            sys.argv = [
                "response_fibre_parametric_preflight_v1_1.py",
                "--outdir",
                "response_fibre_parametric_preflight_results",
            ]
            m.main()
        finally:
            sys.argv = saved_argv
        preflight_path = find_preflight(None)
    preflight = json.loads(preflight_path.read_text(encoding="utf-8"))
    preflight_report = preflight.get("report", {})
    if (
        preflight_report.get("scientific_status")
        != "PARAMETRIC_RESPONSE_FIBRE_PREFLIGHT_SUPPORTED"
        or not preflight_report.get("all_gates_pass", False)
        or preflight_report.get("segments_passing") != 10
        or preflight_report.get("overlaps_passing") != 9
    ):
        raise RuntimeError("The complete v1.1.1 preflight PASS is required.")

    declared_segments = 1 if args.quick else 10
    protocol = {
        "title": TITLE,
        "version": VERSION,
        "formal_interval_arithmetic": True,
        "arb_precision_bits": PRECISION_BITS,
        "model": "14-segment driven qubit with common quasi-static detuning",
        "response_map": "real/imaginary parts of exact projective coefficients a0..a3",
        "control_dimension": 14,
        "response_dimension": 8,
        "declared_segments": declared_segments,
        "subdivisions_per_segment": SUBDIVISIONS,
        "declared_parameter_boxes": declared_segments * SUBDIVISIONS,
        "global_transverse_gauge": True,
        "chebyshev_degree": DEGREE,
        "fit_points": FIT_POINTS,
        "cauchy_points": CAUCHY_POINTS,
        "cauchy_arcs": CAUCHY_ARCS,
        "jet_order": JET_ORDER,
        "sample_radius": SAMPLE_RADIUS,
        "bound_radius": BOUND_RADIUS,
        "root_radius_schedule": list(ROOT_RADII),
        "endpoint_radius": ENDPOINT_RADIUS,
        "loss_jet_order": LOSS_JET_ORDER,
        "loss_sample_radius": LOSS_SAMPLE_RADIUS,
        "loss_bound_radius": LOSS_BOUND_RADIUS,
        "finite_error_window": [FINITE_ERROR_MIN, FINITE_ERROR_MAX],
        "finite_error_bins": FINITE_ERROR_BINS,
        "descent_claim": (
            (
                "strict endpoint-to-endpoint descent for the first declared "
                "curve segment only; quick mode cannot issue the ten-segment "
                "theorem and does not claim pointwise monotonicity in the "
                "curve parameter"
            )
            if args.quick
            else (
                "strict endpoint-to-endpoint descent for all ten declared "
                "curve segments; not pointwise monotonicity in the curve "
                "parameter"
            )
        ),
        "analytic_degeneracy_used_in_loss_difference": (
            "exact equality of projective response coefficients a0..a3 "
            "sets symmetric-loss difference orders 0..5 identically to zero"
        ),
        "exact_target_basis_construction": (
            "the target is the normalized nominal reference state and its "
            "orthogonal complement is constructed algebraically; all pulse "
            "trigonometry uses outward-rounded Arb values of the declared "
            "decimal segment duration"
        ),
        "finite_error_partition": (
            "exact Arb decimal endpoints with contiguous rational subdivision"
        ),
        "krawczyk_preconditioner": (
            "NumPy midpoint inverse frozen as an exact Arb point matrix; "
            "all theorem-bearing products and inclusions are outward-rounded Arb"
        ),
        "formal_krawczyk_linear_algebra": True,
        "source_preflight_sha256": sha256_file(preflight_path),
        "model_solver_source": model_source,
        "finite_error_outcomes_used_to_construct_curve": False,
        "L6_used_to_construct_curve": False,
        "uses_pasqal_credentials": False,
        "uses_cloud_or_qpu": False,
        "quick_mode": bool(args.quick),
    }
    protocol_hash = sha256_bytes(canonical_json(protocol))

    banner(f"{TITLE} v{VERSION}")
    print("No PASQAL account, password, token, API key, or project ID is used.")
    print(json.dumps(protocol, indent=2))
    print(f"protocol_sha256 = {protocol_hash}")

    def ap(x: float):
        return arb(repr(float(x)))

    def upper_point(value):
        """Return an Arb point at a certified upper bound."""
        if isinstance(value, acb):
            value = value.abs_upper()
        if isinstance(value, arb):
            return arb(str(value.abs_upper().upper()))
        return ap(math.nextafter(abs(float(value)), math.inf))

    def ball(mid, radius):
        """Outward-rounded real ball accepting float or Arb inputs."""
        midpoint = mid if isinstance(mid, arb) else ap(mid)
        radius_upper = upper_point(radius).upper()
        return midpoint + arb(0, str(radius_upper))

    class DeltaJet:
        order = 3

        def __init__(self, coefficients=0):
            if isinstance(coefficients, DeltaJet):
                self.c = coefficients.c[:]
            elif isinstance(coefficients, (list, tuple)):
                self.c = [acb(x) for x in coefficients]
                self.c += [acb(0)] * (self.order + 1 - len(self.c))
            else:
                self.c = [acb(coefficients)] + [acb(0)] * self.order
            self.c = self.c[: self.order + 1]

        def __add__(self, other):
            other = DeltaJet(other)
            return DeltaJet(
                [self.c[i] + other.c[i] for i in range(self.order + 1)]
            )

        __radd__ = __add__

        def __neg__(self):
            return DeltaJet([-x for x in self.c])

        def __sub__(self, other):
            return self + (-DeltaJet(other))

        def __rsub__(self, other):
            return DeltaJet(other) - self

        def __mul__(self, other):
            other = DeltaJet(other)
            return DeltaJet(
                [
                    sum(
                        (self.c[k] * other.c[n - k] for k in range(n + 1)),
                        acb(0),
                    )
                    for n in range(self.order + 1)
                ]
            )

        __rmul__ = __mul__

        def inv(self):
            q = [1 / self.c[0]]
            for n in range(1, self.order + 1):
                q.append(
                    -q[0]
                    * sum(
                        (self.c[k] * q[n - k] for k in range(1, n + 1)),
                        acb(0),
                    )
                )
            return DeltaJet(q)

        def __truediv__(self, other):
            return self * DeltaJet(other).inv()

        def sqrt(self):
            q = [self.c[0].sqrt()]
            for n in range(1, self.order + 1):
                q.append(
                    (
                        self.c[n]
                        - sum(
                            (q[k] * q[n - k] for k in range(1, n)), acb(0)
                        )
                    )
                    / (2 * q[0])
                )
            return DeltaJet(q)

        def exp(self):
            q = [self.c[0].exp()]
            for n in range(1, self.order + 1):
                q.append(
                    sum(
                        (k * self.c[k] * q[n - k] for k in range(1, n + 1)),
                        acb(0),
                    )
                    / n
                )
            return DeltaJet(q)

        def sin(self):
            iz = self * acb(0, 1)
            return (iz.exp() - (-iz).exp()) / acb(0, 2)

        def cos(self):
            iz = self * acb(0, 1)
            return (iz.exp() + (-iz).exp()) / 2

    def matvec(matrix, vector):
        return [
            matrix[0][0] * vector[0] + matrix[0][1] * vector[1],
            matrix[1][0] * vector[0] + matrix[1][1] * vector[1],
        ]

    def state_zero(phases):
        half_tau = ap(m.TAU) / 2
        c = acb(half_tau.cos())
        s = acb(half_tau.sin())
        vector = [acb(1), acb(0)]
        for phase in phases:
            phase = acb(phase)
            em = (-acb(0, 1) * phase).exp()
            ep = (acb(0, 1) * phase).exp()
            matrix = [
                [c, -acb(0, 1) * s * em],
                [-acb(0, 1) * s * ep, c],
            ]
            vector = matvec(matrix, vector)
        return vector

    reference_state = state_zero([ap(x) for x in m.REFERENCE_PHASES])
    reference_norm = (
        reference_state[0].conjugate() * reference_state[0]
        + reference_state[1].conjugate() * reference_state[1]
    ).sqrt()
    target = [x / reference_norm for x in reference_state]
    orthogonal = [-target[1].conjugate(), target[0].conjugate()]

    def inner(left, vector):
        return (
            DeltaJet(left[0].conjugate()) * vector[0]
            + DeltaJet(left[1].conjugate()) * vector[1]
        )

    def response_and_reduced_jacobian(phases, transverse):
        delta = DeltaJet([0, 1])
        radius = (1 + delta * delta).sqrt()
        half_tau = ap(m.TAU) / 2
        c = (radius * half_tau).cos()
        s = (radius * half_tau).sin() / radius
        state = [DeltaJet(1), DeltaJet(0)]
        derivatives = [[DeltaJet(0), DeltaJet(0)] for _ in range(14)]
        for index, phase in enumerate(phases):
            phase = acb(phase)
            em = (-acb(0, 1) * phase).exp()
            ep = (acb(0, 1) * phase).exp()
            matrix = [
                [
                    c - acb(0, 1) * s * delta,
                    -acb(0, 1) * s * em,
                ],
                [
                    -acb(0, 1) * s * ep,
                    c + acb(0, 1) * s * delta,
                ],
            ]
            derivative_matrix = [
                [DeltaJet(0), -s * em],
                [s * ep, DeltaJet(0)],
            ]
            old_state = state
            state = matvec(matrix, old_state)
            new_derivatives = []
            for j in range(14):
                value = matvec(matrix, derivatives[j])
                if j == index:
                    local = matvec(derivative_matrix, old_state)
                    value = [value[0] + local[0], value[1] + local[1]]
                new_derivatives.append(value)
            derivatives = new_derivatives
        numerator = inner(orthogonal, state)
        denominator = inner(target, state)
        coordinate = numerator / denominator
        coordinate_derivatives = []
        for derivative in derivatives:
            dn = inner(orthogonal, derivative)
            dd = inner(target, derivative)
            coordinate_derivatives.append(
                (dn * denominator - numerator * dd) / (denominator * denominator)
            )
        values = coordinate.c[:]
        for order in range(4):
            for column in range(8):
                values.append(
                    sum(
                        (
                            coordinate_derivatives[j].c[order]
                            * ap(transverse[j, column])
                            for j in range(14)
                        ),
                        acb(0),
                    )
                )
        return values

    banner("STAGE 0 - RECONSTRUCT AND FREEZE ONE GLOBAL TRANSVERSE GAUGE")
    first_midpoint = m.correct_center(0.5 * (m.FLOW_NODES[0] + m.FLOW_NODES[1]))
    transverse, _ = m.transverse_basis(first_midpoint)
    singular_global = []
    for node in m.FLOW_NODES:
        jacobian = m.jacobian_fd(m.response_feature_float, node)
        singular_global.append(
            float(np.linalg.svd(jacobian @ transverse, compute_uv=False)[-1])
        )
    if min(singular_global) <= 2.0e-3:
        raise RuntimeError("The declared global transverse gauge is ill-conditioned.")

    chebyshev_nodes = np.sort(
        0.5 * (np.cos(np.pi * np.arange(FIT_POINTS) / (FIT_POINTS - 1)) + 1)
    )
    global_segments = []
    warm = np.zeros(8)
    for segment_index in range(declared_segments):
        left = m.FLOW_NODES[segment_index]
        right = m.FLOW_NODES[segment_index + 1]
        corrections = []
        for scalar in chebyshev_nodes:
            predictor = (1.0 - scalar) * left + scalar * right
            _, warm, _ = m.solve_transverse(predictor, transverse, warm)
            corrections.append(warm.copy())
        corrections = np.asarray(corrections)
        coefficients = np.column_stack(
            [
                np.polynomial.chebyshev.chebfit(
                    2.0 * chebyshev_nodes - 1.0,
                    corrections[:, column],
                    DEGREE,
                )
                for column in range(8)
            ]
        )
        global_segments.append(coefficients)
        print(f"[freeze {segment_index + 1:02d}/{declared_segments}] global chart fitted")

    frozen_parameterization = {
        "protocol_sha256": protocol_hash,
        "source_preflight_sha256": protocol["source_preflight_sha256"],
        "transverse_basis": transverse.tolist(),
        "segment_chebyshev_coefficients": [
            coefficients.tolist() for coefficients in global_segments
        ],
        "minimum_node_reduced_singular_value": min(singular_global),
        "finite_error_outcomes_used": False,
        "L6_used": False,
    }
    frozen_hash = sha256_bytes(canonical_json(frozen_parameterization))
    print(f"global_parameterization_sha256 = {frozen_hash}")

    def chebyshev_evaluate(coefficients, scalar):
        b1 = acb(0)
        b2 = acb(0)
        for coefficient in coefficients[:0:-1]:
            b0 = 2 * scalar * b1 - b2 + ap(coefficient)
            b2, b1 = b1, b0
        return scalar * b1 - b2 + ap(coefficients[0])

    def phase_curve(segment_index, scalar, root_radius=0.0):
        coefficients = global_segments[segment_index]
        correction = [
            chebyshev_evaluate(coefficients[:, column], 2 * scalar - 1)
            for column in range(8)
        ]
        phases = []
        left = m.FLOW_NODES[segment_index]
        right = m.FLOW_NODES[segment_index + 1]
        for row in range(14):
            value = (1 - scalar) * ap(left[row]) + scalar * ap(right[row])
            value += sum(
                (
                    ap(transverse[row, column]) * correction[column]
                    for column in range(8)
                ),
                acb(0),
            )
            if root_radius:
                physical_radius = sum(
                    (
                        upper_point(transverse[row, column])
                        * upper_point(root_radius)
                        for column in range(8)
                    ),
                    arb(0),
                )
                value += acb(ball(0, physical_radius))
            phases.append(value)
        return phases

    target_response = response_and_reduced_jacobian(
        [ap(x) for x in m.REFERENCE_PHASES], transverse
    )[:4]

    def add_disk(value, radius):
        error = ball(0, radius)
        return value + acb(error, error)

    def enclose(segment_index, center, half_width, root_radius, only_feature):
        count = 4 if only_feature else 36
        samples = []
        sample_roots = []
        pi_ball = arb.pi()
        sample_radius_ball = ap(SAMPLE_RADIUS)
        bound_radius_ball = ap(BOUND_RADIUS)
        for sample_index in range(CAUCHY_POINTS):
            angle = 2 * pi_ball * sample_index / CAUCHY_POINTS
            root = acb(angle.cos(), angle.sin())
            sample_roots.append(root)
            scalar = acb(ap(center)) + sample_radius_ball * root
            samples.append(
                response_and_reduced_jacobian(
                    phase_curve(segment_index, scalar, root_radius), transverse
                )[:count]
            )

        bounds = [arb(0) for _ in range(count)]
        angular_half_width = pi_ball / CAUCHY_ARCS
        for arc_index in range(CAUCHY_ARCS):
            angle = ball(
                pi_ball * (2 * arc_index + 1) / CAUCHY_ARCS,
                angular_half_width,
            )
            scalar = acb(ap(center)) + bound_radius_ball * acb(
                angle.cos(), angle.sin()
            )
            values = response_and_reduced_jacobian(
                phase_curve(segment_index, scalar, root_radius), transverse
            )[:count]
            for index, value in enumerate(values):
                bound_value = upper_point(value)
                if not math.isfinite(float(bound_value)):
                    raise ArithmeticError(
                        "The analytic Cauchy boundary enclosure is non-finite."
                    )
                if bound_value > bounds[index]:
                    bounds[index] = bound_value

        local = acb(ball(0, half_width))
        outputs = []
        radius_ratio = sample_radius_ball / bound_radius_ball
        alias_factor = (
            radius_ratio**CAUCHY_POINTS
            / (1 - radius_ratio**CAUCHY_POINTS)
        )
        for output_index in range(count):
            coefficients = []
            for order in range(JET_ORDER + 1):
                total = acb(0)
                for sample_index in range(CAUCHY_POINTS):
                    total += (
                        samples[sample_index][output_index]
                        * sample_roots[sample_index].conjugate() ** order
                    )
                coefficient = total / (
                    CAUCHY_POINTS * sample_radius_ball**order
                )
                coefficient = add_disk(
                    coefficient,
                    bounds[output_index]
                    / bound_radius_ball**order
                    * alias_factor,
                )
                coefficients.append(coefficient)
            value = coefficients[-1]
            for coefficient in coefficients[-2::-1]:
                value = value * local + coefficient
            half_width_ball = ap(half_width)
            tail = (
                bounds[output_index]
                / bound_radius_ball ** (JET_ORDER + 1)
                * half_width_ball ** (JET_ORDER + 1)
                / (1 - half_width_ball / bound_radius_ball)
            )
            outputs.append(add_disk(value, tail))
        return outputs

    def krawczyk_box(segment_index, center, half_width, root_radius):
        feature = enclose(segment_index, center, half_width, 0.0, True)
        jacobian_values = enclose(
            segment_index, center, half_width, root_radius, False
        )
        feature_ball = []
        feature_mid = []
        feature_rad = []
        for order in range(4):
            difference = feature[order] - target_response[order]
            for component in (difference.real, difference.imag):
                feature_ball.append(component)
                mid, rad = midpoint_radius(component)
                feature_mid.append(mid)
                feature_rad.append(rad)

        jacobian_ball = [
            [arb(0) for _ in range(8)] for _ in range(8)
        ]
        jacobian_mid = np.zeros((8, 8))
        offset = 4
        for order in range(4):
            for column in range(8):
                value = jacobian_values[offset]
                offset += 1
                for component_index, component in enumerate(
                    (value.real, value.imag)
                ):
                    row = 2 * order + component_index
                    jacobian_ball[row][column] = component
                    jacobian_mid[row, column] = midpoint_radius(component)[0]

        # A floating-point inverse is permitted as an arbitrary Krawczyk
        # preconditioner.  It is immediately frozen as an exact Arb point
        # matrix; every theorem-bearing product below is outward-rounded.
        inverse_float = np.linalg.inv(jacobian_mid)
        preconditioner = [
            [ap(inverse_float[row, column]) for column in range(8)]
            for row in range(8)
        ]
        correction = [
            -sum(
                (
                    preconditioner[row][column] * feature_ball[column]
                    for column in range(8)
                ),
                arb(0),
            )
            for row in range(8)
        ]
        defect = [
            [
                arb(int(row == column))
                - sum(
                    (
                        preconditioner[row][inner]
                        * jacobian_ball[inner][column]
                        for inner in range(8)
                    ),
                    arb(0),
                )
                for column in range(8)
            ]
            for row in range(8)
        ]
        root_box = ball(0, root_radius)
        images = [
            correction[row]
            + sum(
                (
                    defect[row][column] * root_box
                    for column in range(8)
                ),
                arb(0),
            )
            for row in range(8)
        ]
        image_upper_bounds = [upper_point(value) for value in images]
        ratio_upper_bounds = [
            value / ap(root_radius) for value in image_upper_bounds
        ]
        inclusion_ratio_ball = max(ratio_upper_bounds)
        defect_row_bounds = [
            sum(
                (upper_point(value) for value in row),
                arb(0),
            )
            for row in defect
        ]
        defect_bound_ball = max(defect_row_bounds)
        strict_inclusion = all(
            value < ap(root_radius) for value in image_upper_bounds
        )
        contraction_pass = defect_bound_ball < arb(1)
        return {
            "pass": bool(strict_inclusion and contraction_pass),
            "root_radius": root_radius,
            "inclusion_ratio": float(inclusion_ratio_ball),
            "right_inverse_defect_bound": float(defect_bound_ball),
            "strict_arb_inclusion": bool(strict_inclusion),
            "arb_contraction_pass": bool(contraction_pass),
            "formal_arb_linear_algebra": True,
            "midpoint_minimum_singular_value": float(
                np.linalg.svd(jacobian_mid, compute_uv=False)[-1]
            ),
            "maximum_feature_radius": max(feature_rad),
            "maximum_feature_midpoint_residual": max(
                map(abs, feature_mid), default=0.0
            ),
        }

    banner("STAGE 1 - PARAMETER-DEPENDENT ARB KRAWCZYK CHAIN")
    start_time = time.time()
    boxes = []
    for segment_index in range(declared_segments):
        for subdivision in range(SUBDIVISIONS):
            center = (subdivision + 0.5) / SUBDIVISIONS
            half_width = 0.5 / SUBDIVISIONS
            accepted = None
            for radius in ROOT_RADII:
                result = krawczyk_box(
                    segment_index, center, half_width, radius
                )
                if result["pass"]:
                    accepted = result
                    break
            if accepted is None:
                accepted = result
            accepted.update(
                {
                    "segment": segment_index,
                    "subdivision": subdivision,
                    "parameter_interval": [
                        subdivision / SUBDIVISIONS,
                        (subdivision + 1) / SUBDIVISIONS,
                    ],
                }
            )
            boxes.append(accepted)
            print(
                f"[box {len(boxes):04d}/{declared_segments * SUBDIVISIONS}] "
                f"pass={accepted['pass']} "
                f"ratio={accepted['inclusion_ratio']:.4f} "
                f"defect={accepted['right_inverse_defect_bound']:.4f}"
            )

    banner("STAGE 2 - SHARED-ENDPOINT CONTINUATION")
    overlaps = []
    if not args.quick:
        for endpoint in range(1, 10):
            left_coefficients = global_segments[endpoint - 1]
            right_coefficients = global_segments[endpoint]
            left_correction = [
                chebyshev_evaluate(
                    left_coefficients[:, column], acb(1)
                ).real
                for column in range(8)
            ]
            right_correction = [
                chebyshev_evaluate(
                    right_coefficients[:, column], acb(-1)
                ).real
                for column in range(8)
            ]
            center_gap_ball = max(
                (
                    upper_point(left_correction[column] - right_correction[column])
                    for column in range(8)
                ),
                default=arb(0),
            )
            center_gap = float(center_gap_ball)
            # The shared endpoint equation uses the same predictor and the
            # same global transverse gauge.  A larger Krawczyk box containing
            # both neighboring root boxes proves that the two local branches
            # meet at the same unique exact root.
            endpoint_result = krawczyk_box(
                endpoint - 1, 1.0, 0.0, ENDPOINT_RADIUS
            )
            left_box_radius = boxes[endpoint * SUBDIVISIONS - 1][
                "root_radius"
            ]
            right_box_radius = boxes[endpoint * SUBDIVISIONS]["root_radius"]
            contained = (
                ap(left_box_radius) < ap(ENDPOINT_RADIUS)
                and center_gap_ball + ap(right_box_radius) < ap(ENDPOINT_RADIUS)
            )
            endpoint_result.update(
                {
                    "endpoint": endpoint,
                    "neighbor_center_gap_upper_bound": center_gap,
                    "neighbor_boxes_contained": bool(contained),
                    "pass": bool(endpoint_result["pass"] and contained),
                }
            )
            overlaps.append(endpoint_result)
            print(
                f"[overlap {endpoint:02d}/09] "
                f"pass={endpoint_result['pass']} "
                f"gap={center_gap:.3e} "
                f"ratio={endpoint_result['inclusion_ratio']:.4f}"
            )

    banner("STAGE 3 - EXACT-ROOT L6 AND FINITE-WINDOW DESCENT")

    def direct_state(phases, delta):
        delta = acb(delta)
        radius = (1 + delta * delta).sqrt()
        half_tau = ap(m.TAU) / 2
        c = (radius * half_tau).cos()
        s = (radius * half_tau).sin() / radius
        vector = [acb(1), acb(0)]
        for phase in phases:
            phase = acb(phase)
            em = (-acb(0, 1) * phase).exp()
            ep = (acb(0, 1) * phase).exp()
            matrix = [
                [c - acb(0, 1) * s * delta, -acb(0, 1) * s * em],
                [-acb(0, 1) * s * ep, c + acb(0, 1) * s * delta],
            ]
            vector = matvec(matrix, vector)
        return vector

    def projective_coordinate_direct(phases, delta):
        vector = direct_state(phases, delta)
        numerator = sum(
            (
                orthogonal[index].conjugate() * vector[index]
                for index in range(2)
            ),
            acb(0),
        )
        denominator = sum(
            (
                target[index].conjugate() * vector[index]
                for index in range(2)
            ),
            acb(0),
        )
        return numerator / denominator

    def analytic_projective_loss(phases, delta):
        # For real delta this is |z(delta)|^2/(1+|z(delta)|^2).
        # zbar(delta)=conj(z(conj(delta))) is its holomorphic continuation.
        delta = acb(delta)
        z = projective_coordinate_direct(phases, delta)
        zbar = projective_coordinate_direct(
            phases, delta.conjugate()
        ).conjugate()
        q = z * zbar
        return q / (1 + q)

    def analytic_symmetric_loss(phases, delta):
        delta = acb(delta)
        return (
            analytic_projective_loss(phases, delta)
            + analytic_projective_loss(phases, -delta)
        ) / 2

    def loss_difference(after_phases, before_phases, delta):
        return analytic_symmetric_loss(
            after_phases, delta
        ) - analytic_symmetric_loss(before_phases, delta)

    def loss_difference_taylor(after_phases, before_phases):
        pi_ball = arb.pi()
        sample_radius = ap(LOSS_SAMPLE_RADIUS)
        bound_radius = ap(LOSS_BOUND_RADIUS)
        roots = []
        samples = []
        for sample_index in range(CAUCHY_POINTS):
            angle = 2 * pi_ball * sample_index / CAUCHY_POINTS
            root = acb(angle.cos(), angle.sin())
            roots.append(root)
            samples.append(
                loss_difference(
                    after_phases,
                    before_phases,
                    sample_radius * root,
                )
            )

        boundary_bound = arb(0)
        angular_half_width = pi_ball / CAUCHY_ARCS
        for arc_index in range(CAUCHY_ARCS):
            angle = ball(
                pi_ball * (2 * arc_index + 1) / CAUCHY_ARCS,
                angular_half_width,
            )
            delta = bound_radius * acb(angle.cos(), angle.sin())
            candidate = upper_point(
                loss_difference(after_phases, before_phases, delta)
            )
            if candidate > boundary_bound:
                boundary_bound = candidate

        radius_ratio = sample_radius / bound_radius
        alias_factor = (
            radius_ratio**CAUCHY_POINTS
            / (1 - radius_ratio**CAUCHY_POINTS)
        )
        coefficients = []
        for order in range(LOSS_JET_ORDER + 1):
            total = sum(
                (
                    samples[sample_index]
                    * roots[sample_index].conjugate() ** order
                    for sample_index in range(CAUCHY_POINTS)
                ),
                acb(0),
            )
            coefficient = total / (
                CAUCHY_POINTS * sample_radius**order
            )
            coefficient = add_disk(
                coefficient,
                boundary_bound / bound_radius**order * alias_factor,
            )
            coefficients.append(coefficient)
        return coefficients, boundary_bound

    def evaluate_loss_difference(coefficients, boundary_bound, delta):
        delta = acb(delta)
        value = coefficients[-1]
        for coefficient in coefficients[-2::-1]:
            value = value * delta + coefficient
        delta_upper = upper_point(delta)
        bound_radius = ap(LOSS_BOUND_RADIUS)
        tail = (
            boundary_bound
            / bound_radius ** (LOSS_JET_ORDER + 1)
            * delta_upper ** (LOSS_JET_ORDER + 1)
            / (1 - delta_upper / bound_radius)
        )
        return add_disk(value, tail).real, tail

    endpoint_roots = []
    endpoint_root_results = []
    for node_index in range(declared_segments + 1):
        if node_index == 0:
            segment_index = 0
            scalar = 0.0
        else:
            segment_index = node_index - 1
            scalar = 1.0
        root_result = krawczyk_box(
            segment_index, scalar, 0.0, ENDPOINT_RADIUS
        )
        endpoint_root_results.append(root_result)
        endpoint_roots.append(
            phase_curve(
                segment_index,
                acb(ap(scalar)),
                ENDPOINT_RADIUS,
            )
        )
        print(
            f"[endpoint {node_index:02d}/{declared_segments:02d}] "
            f"pass={root_result['pass']} "
            f"ratio={root_result['inclusion_ratio']:.4f}"
        )

    descent_segments = []
    finite_error_min_arb = ap(FINITE_ERROR_MIN)
    finite_error_max_arb = ap(FINITE_ERROR_MAX)
    finite_error_step_arb = (
        finite_error_max_arb - finite_error_min_arb
    ) / FINITE_ERROR_BINS
    for segment_index in range(declared_segments):
        coefficients, boundary_bound = loss_difference_taylor(
            endpoint_roots[segment_index + 1],
            endpoint_roots[segment_index],
        )
        l2 = coefficients[2].real
        l4 = coefficients[4].real
        l6 = coefficients[6].real
        low_order_zero_checks = [
            bool(coefficients[order].real.contains(0))
            for order in range(6)
        ]
        # This is an analytic substitution, not a numerical truncation:
        # exact matching of a0..a3 fixes the symmetric loss through degree
        # four, while symmetrization removes every odd degree.  Therefore the
        # difference coefficients of degrees 0,...,5 vanish identically.
        degenerate_coefficients = [
            acb(0) if order < 6 else coefficient
            for order, coefficient in enumerate(coefficients)
        ]
        bin_records = []
        for bin_index in range(FINITE_ERROR_BINS):
            left = finite_error_min_arb + bin_index * finite_error_step_arb
            right = (
                finite_error_min_arb
                + (bin_index + 1) * finite_error_step_arb
            )
            delta = ball(
                (left + right) / 2,
                (right - left) / 2,
            )
            difference, tail = evaluate_loss_difference(
                degenerate_coefficients, boundary_bound, delta
            )
            bin_records.append(
                {
                    "bin": bin_index,
                    "interval": [float(left), float(right)],
                    "difference_lower": float(difference.lower()),
                    "difference_upper": float(difference.upper()),
                    "tail_upper": float(upper_point(tail)),
                    "strict_descent": bool(difference < arb(0)),
                }
            )
        segment_pass = (
            endpoint_root_results[segment_index]["pass"]
            and endpoint_root_results[segment_index + 1]["pass"]
            and l2.contains(0)
            and l4.contains(0)
            and all(low_order_zero_checks)
            and l6 < arb(0)
            and all(item["strict_descent"] for item in bin_records)
        )
        record = {
            "segment": segment_index,
            "pass": bool(segment_pass),
            "endpoint_roots_pass": bool(
                endpoint_root_results[segment_index]["pass"]
                and endpoint_root_results[segment_index + 1]["pass"]
            ),
            "L2_difference_contains_zero": bool(l2.contains(0)),
            "L4_difference_contains_zero": bool(l4.contains(0)),
            "orders_0_to_5_contain_zero_before_analytic_substitution": (
                low_order_zero_checks
            ),
            "analytic_orders_0_to_5_set_exactly_to_zero": True,
            "L6_difference_lower": float(l6.lower()),
            "L6_difference_upper": float(l6.upper()),
            "L6_strict_descent": bool(l6 < arb(0)),
            "boundary_modulus_upper": float(boundary_bound),
            "finite_error_bins": bin_records,
            "all_finite_error_bins_strictly_decrease": all(
                item["strict_descent"] for item in bin_records
            ),
            "maximum_finite_error_difference_upper": max(
                item["difference_upper"] for item in bin_records
            ),
        }
        descent_segments.append(record)
        print(
            f"[descent {segment_index + 1:02d}/{declared_segments:02d}] "
            f"pass={record['pass']} "
            f"L6_upper={record['L6_difference_upper']:.3e} "
            f"finite_max_upper="
            f"{record['maximum_finite_error_difference_upper']:.3e}"
        )

    all_boxes_pass = len(boxes) == declared_segments * SUBDIVISIONS and all(
        item["pass"] for item in boxes
    )
    all_overlaps_pass = args.quick or (
        len(overlaps) == 9 and all(item["pass"] for item in overlaps)
    )
    all_endpoint_roots_pass = (
        len(endpoint_root_results) == declared_segments + 1
        and all(item["pass"] for item in endpoint_root_results)
    )
    all_descent_segments_pass = (
        len(descent_segments) == declared_segments
        and all(item["pass"] for item in descent_segments)
    )
    full_cohort = not args.quick
    all_gates_pass = (
        all_boxes_pass
        and all_overlaps_pass
        and all_endpoint_roots_pass
        and all_descent_segments_pass
        and full_cohort
    )
    status = (
        "EXACT_ROOT_STEPWISE_FINITE_ERROR_DESCENT_FORMALLY_CERTIFIED"
        if all_gates_pass
        else (
            "QUICK_PREFLIGHT_ONLY"
            if (
                args.quick
                and all_boxes_pass
                and all_endpoint_roots_pass
                and all_descent_segments_pass
            )
            else "EXACT_ROOT_STEPWISE_DESCENT_INCONCLUSIVE"
        )
    )
    scope = (
        "validated connected local response-matched curve with strict "
        "endpoint-to-endpoint finite-window descent in the serialized "
        "driven-qubit model; not pointwise parameter monotonicity, a "
        "global fibre, geometric memory, PASQAL Cloud, or a QPU theorem"
        if all_gates_pass
        else
        "validated connected local response-matched curve; exact-root L6 "
        "and finite-window descent are reported as separate fail-closed "
        "gates, and finite-window descent is not claimed unless every "
        "declared segment passes"
    )
    report = {
        "scientific_status": status,
        "formal_interval_arithmetic": True,
        "formal_krawczyk_linear_algebra": True,
        "floating_inverse_used_only_as_preconditioner": True,
        "arb_precision_bits": PRECISION_BITS,
        "global_parameterization_sha256": frozen_hash,
        "parameter_boxes_certified": sum(item["pass"] for item in boxes),
        "parameter_boxes_declared": declared_segments * SUBDIVISIONS,
        "shared_endpoints_certified": sum(item["pass"] for item in overlaps),
        "shared_endpoints_declared": 0 if args.quick else 9,
        "maximum_krawczyk_inclusion_ratio": max(
            (item["inclusion_ratio"] for item in boxes), default=float("inf")
        ),
        "maximum_right_inverse_defect_bound": max(
            (item["right_inverse_defect_bound"] for item in boxes),
            default=float("inf"),
        ),
        "minimum_midpoint_singular_value": min(
            (item["midpoint_minimum_singular_value"] for item in boxes),
            default=0.0,
        ),
        "all_parameter_boxes_pass": all_boxes_pass,
        "all_shared_endpoints_pass": all_overlaps_pass,
        "endpoint_root_boxes_certified": sum(
            item["pass"] for item in endpoint_root_results
        ),
        "endpoint_root_boxes_declared": declared_segments + 1,
        "all_endpoint_root_boxes_pass": all_endpoint_roots_pass,
        "descent_segments_certified": sum(
            item["pass"] for item in descent_segments
        ),
        "descent_segments_declared": declared_segments,
        "L6_descent_segments_certified": sum(
            item["L6_strict_descent"] for item in descent_segments
        ),
        "finite_error_descent_segments_certified": sum(
            item["all_finite_error_bins_strictly_decrease"]
            for item in descent_segments
        ),
        "all_stepwise_L6_and_finite_error_descent_pass": (
            all_descent_segments_pass
        ),
        "finite_error_window": [FINITE_ERROR_MIN, FINITE_ERROR_MAX],
        "finite_error_bins_per_segment": FINITE_ERROR_BINS,
        "maximum_certified_L6_difference_upper": max(
            (
                item["L6_difference_upper"]
                for item in descent_segments
            ),
            default=float("inf"),
        ),
        "maximum_certified_finite_error_difference_upper": max(
            (
                item["maximum_finite_error_difference_upper"]
                for item in descent_segments
            ),
            default=float("inf"),
        ),
        "full_declared_chain": full_cohort,
        "global_six_dimensional_fibre_claimed": False,
        "holonomy_claimed": False,
        "pointwise_curve_parameter_monotonicity_claimed": False,
        "stepwise_exact_root_finite_error_descent_claimed": bool(
            all_gates_pass
        ),
        "protocol_sha256": protocol_hash,
        "elapsed_seconds": time.time() - start_time,
        "scope": scope,
    }

    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    (output / "protocol.json").write_bytes(
        json.dumps(protocol, indent=2, sort_keys=True).encode("utf-8") + b"\n"
    )
    (output / "global_parameterization.json").write_bytes(
        json.dumps(
            frozen_parameterization, indent=2, sort_keys=True
        ).encode("utf-8")
        + b"\n"
    )
    certificate = {
        "protocol": protocol,
        "global_parameterization_sha256": frozen_hash,
        "boxes": boxes,
        "overlaps": overlaps,
        "endpoint_root_boxes": endpoint_root_results,
        "descent_segments": descent_segments,
        "report": report,
        "versions": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "python_flint": "0.8.0",
        },
    }
    certificate_bytes = (
        json.dumps(certificate, indent=2, sort_keys=True).encode("utf-8")
        + b"\n"
    )
    (output / "certificate.json").write_bytes(certificate_bytes)
    report["certificate_sha256"] = sha256_bytes(certificate_bytes)
    (output / "report.json").write_bytes(
        json.dumps(report, indent=2, sort_keys=True).encode("utf-8") + b"\n"
    )

    banner("FINAL RESULT")
    print(json.dumps(report, indent=2))
    print("\nInterpretation")
    if all_gates_pass:
        print(
            "  PASS: the connected exact response-matched curve is certified, "
            "and every declared endpoint-to-endpoint step strictly decreases "
            "both L6 and the symmetric finite-error loss throughout the "
            "complete declared error window."
        )
        print(
            "  This is a stepwise endpoint theorem. It does not certify "
            "pointwise monotonicity at every curve parameter, a global "
            "six-dimensional response fibre, or holonomy."
        )
    elif (
        args.quick
        and all_boxes_pass
        and all_endpoint_roots_pass
        and all_descent_segments_pass
    ):
        print(
            "  QUICK PASS: the first exact-root segment and its finite-window "
            "descent close, but quick mode cannot issue the full theorem."
        )
    else:
        print(
            "  INCONCLUSIVE: at least one curve, endpoint-root, L6, or "
            "finite-window descent gate failed. Do not claim the combined "
            "exact-root descent theorem."
        )


if __name__ == "__main__":
    main()
