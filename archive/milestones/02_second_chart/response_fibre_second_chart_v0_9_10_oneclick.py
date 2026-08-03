#!/usr/bin/env python3
"""Formal second local fibre-chart/Picard audit v0.9.10.

Requires the v0.9.9 one-click file in the same Colab directory.  The program
instruments that frozen chain so the original Arb graph/metric/Picard backend
continues from the v0.9.8 corrected centre using the v0.9.9 certified frame.
It also checks inclusion of the frozen v0.9.6 endpoint enclosure.
"""
from __future__ import annotations
import argparse,base64,hashlib,json,platform,subprocess,sys,time,zlib
from decimal import Decimal,getcontext
from pathlib import Path

VERSION="0.9.10"
TITLE="GEOMETRIC-FLOW FORMAL SECOND LOCAL FIBRE-CHART CONTINUATION"
V099="archive/milestones/02_second_chart/response_fibre_recentered_frame_v0_9_9_oneclick.py"
V099_SHA="5c95b625279c024168123b9ff0ca11451feb43794ce926f518920b6b4380ed10"
EMBEDDED_V099_ZLIB_B64="""eNqtetly4ti24Ht+BZf7cOzGaQQSQspq32hNgJCQQCOQXUFoRvM8VtS/9wacQ1VlnlvV3XYYI+2117TXKK3//I9pXRZT00+mTtKMsr66pgn8YTwey5WR2EaUJs7ITYvYiEaFYzlJ5RSO/dEtjNgZGbXtV7fV0dpJY6cqfOvjKkrbUQO94uD3wwcmNh27HFVXgKRIByd5GVVOWTn2AwQb2YXfOMXLyLABmJGMiMIcfY/cqEZ+VX7gCqO1hj78aDlF5bs+QFCkaTUy0w7sTcCVU9TJg1DhZGnpV2nRf0yMCqAfZQDWHVlXw09eb6J9ALzEo8vFrau6cC6XkR9naQGIJUlagS1pUn74cqvwMqMonRfTKB0Uebka5TXyzZegTJOXtHzJIqO6qeelrE1AxnLK8qXsy5fKj52XAUA+aGVGddv2hdAeXH74oDGSzIrC2/iurfEHhVV45m28ZsQdo0gs9XHFi/poJUo7gh9JDMUICiMx9EghhDX4/lF4rKwkYseMCJVmlfEHZkcyNM3QF3lDvI1RFHUNG0Ec3IaXEAKuEBhDIctGHAhxTBPBlijuWjMbn7sYZpouDC5g3MIc1JhZtvkN39u//vUvR8hnYlwpyODP4emuELbI/gRby60XLcK1jGmH3oZjfUPIabs3VTia8dsq6xFL7/ebjjKQYtqIZx6TCQ8ahI5f6aQJVatFgx5cd/DSslEIymDpTTWXFtTK7ezVVcZFSFSnPr8LApxj7FLpEWRyQGzVU7N5qVfVDhnCUL/CFraVh/1EKba+NEkWWww7NjuMtof5YqAmW9iyjXlr6was46dcGRiIjvmzPzdSAW3ZKUIm25NF7pE5hoXZbt+ft5v9Wm8LKKa4XaOcynmwp3bkNDy79bkaCkQ/ibseX5yZzXyxQ5D0oB0zYthOpHBlOfA2ZtrFziyy3fW6gs4TxY7xyQS+Rg3N0o5YynTiz6fZKpnUxKFE0AUlLqYllVLT6X4/eGvjLPQdTbGKkuqsYRNs21ABRTDLECJMQjkRplqaW3iYDL3oEw1L1K3HdqvNIleITpIOW6/vCJbs+soJfYZzZIcP2AJP8oNl8TK7l7nyQNvnkjsQXeivNp49WYXw2ptdLX7voGueOLKqrzC+Ak4vh1bLVavIDeSTfZqRKsUSARH6ye5wJruo0MwFr0Exv5sjnHGQyRTNzmmzKWahFcuKqGw5hifseaHCDKtGwWpJbRati4StXegrNGTlvlObRdKagpVmVLth1vpkNqXybmA3C9bTM9MNUHGj1Q1vbhYzJ1nVBrS9VoI5Q93jeRDMiWg2iHk84fthlrkDupywO2uAsSuGJ9vlvkOFDMfZ2jpi+EQc8GLwkaqwEq0jAwqaJd3c0VdFPnT7skzIVuFZDdECT0KsLdVd9XNrmesy5elgki6QfcO7YezzQS5VG/EUDJGjbozuzOh1xZ/hjl0sd4OOVTLe05F+2O4W1WG/IUmCIFLSv/aIQKxWsjJH6aqFhoRzIL4UN7ZAc3B0YLnlxNa74toi08V2JlXDFJoeENcmzpMFdr26ooRsHFScCkvJoQmH3g9OKmBnPLQmZ+Dn0HnTiPpwwM+DNGe0UzpFeZSn1dR0YNGE9pjnh/IqPPHUDtpZUiztS26NEF4pJmiKLs0N7OwbblnY5vw673DELO3AVU7ohhy6ZRykO9EQa3x+dVpJmSqIiWN2iRLQJoXWDYLsUgXDGnc50VHiIMVrce53m1JED3he9+c+TPSqJ7JZmzFONcBBamymJQ07kLi3lYaGdNrCB+AgmJs0zsoT6cI/tAtiEjp2a3j7hhWnRV1SOXbetJPVwehghYHra+U2OqLTBxRBNywmdTMR7uwEZCSt2K89aAnby6tFe0aAuMHySk3oCb1MFdWxVWODcTOYpA82Xh/hVcm4hT4l4d06FSa9MKnguqYFOZ8WOuSs2/2wLFuzEFOhnG44n8RLAiXJhFKKWecOBLYOM0RA53oHz+Xi7It2IJDGsDGmLc0nS4XtIzM2rBViDrQa6DHvEeSxLY1SFNdSkeviOaeOmL4msZ3mOdIaUc7LnNXK5SZrkNN2uoOW5XSKD8WaMwLDOodnSd92MFeL0Il3SQ0JWL8syKPr7BiZBt68XRVeEK4KAxt2832IEtZuRe+m5MTiROK6abe616CzspE3x0VYJUfAm9B4cZ/sDBgp56dF3TArvz5Q21RrrnhJbiR+n0xVfuv7hLpsh2W29w65gUHzOoXqvllz9pnOPRCcvF2+t5ZZeHbILdp3U9X2WwZBD5I/Gfb8rkcwbbOEIU+ZtyzfbuPFUezjXNxJnbfPr3Mqd8ojtN/MCMVPm+3BSPxQ4CmiWiR14adoJFEZMiEwm+MO3snrzHIYZkwyxy062DQV7hWHBHEWi6nUY1NZYJCVucXTg7tte1xkr12KYNduRcZLTU/LVXy6+vOAE6Oe2QjdoT/jWEkymryKZWtgS3Zj8qeDbYtbOc3zwlrVhWl7p8A6OBIb+vxq7nG+nG0sENwWk/ikhQmk6ZGcuodI3EiH0saOtt6m5M4+HH2Kdy3eOlhSpLotXMoWVXO9cd27/XYztYgmYPJlvo9JnLFrqlC1EyHWc8kjxYmunOJeWxfw0G/Z+oQuAkHJI9ZSGB7JIglzD1LVSlSMBNpuj7E7UW2h4hSXE/fsxtWMjjlm3XFlQJCnsyX0Z5kp0LnM1SWKnBHsCKld2dGeMlDXcOK1VU3OUv642u2kBZm3k+uamtsimawzjpRdXuRtvug5+AoUPGcLZq8VgQEVwAP3rFgGOr+xj22+Y3ty31Mk5VRCdmVFT5+I2XSA0Bp1BsyfwooyTO2T0tMwccYmClqH6/nNJNaO5+nR3G1InKNQ1VLVwTf5le+bbU/ihFFtD2chEFFKYBEdRCOLLFdEvVz3W2IgCGYQ6u26UC0CIs+n41olSHaH6afiTC4wx1WSyfRwVbV81juLjBbr3Ld6ojtxmRLOHU6ZgwSC7/dZ725mNGkFc2M2PWqA31LyxT1jU5tJWpIdQYnF0Tu7TEo2kY3PYNE3JW23TICdLcDvoLhUS0qhvDcTROAFBTulrTuTzhNOhhbxiTvOdZPN3M1xk8KsNJE3/JZJopJaC7lw3socckwpo2SHUw9yt9thuzZcLXfM9cSzYi6smz3nev3aF0zD0GODdPONwim21SY8RknAqifeCg7tmI8nqW3LK/GkgPSP5f7WdpMSbXh/KhZrc35yF4XAuvtGqL30pHml5wY56qZwP4NYgrZabFEpjZSE3l7eTRegViyaJUrDvXduDVxfciS5Jla0dXKIIDusQ55sEpL0QmqVk/Tmel1cd2gLRxDqrUW2pBrWaIWjdECzXa1R2YEL9WiyINWZr8YZLaFZdRggKyRJTfS52M9yblcoUlddqR2tFrMir4EnNz6KwYf1bEuZXYWpfTeJG2ER2+HaM1XPQAO7S3dG31WyGIRI06FuslrvF/BECJqNXMrIXN7uWL4TYnnLHBqTp3Sq4/lpUCTo1MsPKy6KBtUSTiTtVn4EwnRaqvOTEJaMI6yjgFuaWB8NoGA3TIOmlyulJPyTIvH2OiHi6zYrh5Nmts1gS5t8cByOKtb0SS1c1Zgx+Fza+JbaR7lZHjSs5BIsSgxPDGeUvPTgOMnXHcp3lLDliyZc1OhSn6Ggu1IOGDDO5ZJZ8YMcF3tO8KKWtBiXnC4bRCb6YBMFuHg9eYHkOfLqqla8s9bsnZ2VHDxEeqYZs2y/92oPORIp3QUp0VV4vvCPwlmuSFzZhsqO0sneGCRBqQlejUJTPRqr9MB6R5lZzwWpaCvDjLI53wX8QkEJdTelovo4gSJlOiGhJEuQIN00JyO7LoNjiy9y+DTBBjO3VWbYYHEcLpeDUtmzeH6a8UvlaFamEM0CVy60elbqU71rlGlDbK5xLmNZN5yO5iC7cRqzhLhfG6dcEhGQZDd2OfG1o3Sc8HJIz9twHVdOpWH7k74tdGNy1Zo+CaZHl4F5SxzsmTilIXZBIcGGkzRrvtqqCFzVE2SGxvNlYaoaEx/8lJ57JchD4iw62MxAMfNiNhGuGcrEU6egQMWqVkdvYzfQ4oyU3W5VE5gMDCzatdczse5FFVvtRLlmXUK2D2XYkKC78dbemt2Z2ToCfkvyXWn5tJgdl020LfvlKetkeLbLCmVfLEiyl/tyv63EhjpGHE1eV6yg7gKtJu0wTeYkbZYVlBX6dXsKl7sEodi6qE55sLU726sqYb7XRa9Jorg2VG8GEVYKl5pdp6lYTeU9y2xxk6VOGpVLcTQsSHHrTaxQqMQNa6PqPJpIPml3xs5ddzpvsukmlEqd9S0BS/vNvjrtbJSPjtCBXO2ScA1NA04hxO1hMnjK5MBTlbchER6S9hspaHYtM5gszKj70l83ktOeJSlh6PW2nc30s3CFpRmI5hvAY0PDEWjYD+qyJqABwwBtiVprHRRaXVhiLAXCfLUxKGUpT7boJsG59ZSCly4VMt25gReZDYpHUXalwxLx+oop9SWjxpJ2XNAHXVwasXjl4wVeVCzVoEZm7i3Qq9QhtNUIxjo7M4WaczOKVbckpOxSTiZluDZRs4nn+bCD1WKDJjSDaRHFnwnoYGhZcjSpeYkm8FI9ro493mrHQahSf16ULeMOrZlzQlRHwlDp6JEgB+4UZbMwLZO+EXuaWHaxBlQmbvRWPZwJAt+IVkjblZVE7ubc+ynnN4vOOc50L/cyNh76owHqcW4vZPCR8+d7/krszxKD5XqnHnOrpENzgW9PYtqilUVMp0bn5aHI9L7DQMNkWieEiqkaR+uz/sCp2BkSMgL8ioeTuThMyYQQAh2K+2N5lC3QkSNrap+IEOEpuFKspINkbvfcLAA9vxCHgYYtkOtsSXNZute3vm4tIifQIyjfr+F1vrURCHgt1nGs1kbpVSBwgpOVVGZFcrPizqqEEucDpw36SbBLBp1vBQ4mTpuT0LApr5osea4937w2DEfNm00WwnM3QVaOdAQHm9CWBPr1zhXrtJtpmp/BtLuKOU9fwsF8naa7ZHa48pW0vyoUaLZsAZ/NTSXyF/wyZ8Sts0UkK657hp/ldCs5cocTq1LfaYWmrVncV3hfwktsL1u1z+bKfH3ymDO9s4oWpmM6JOAOiTirILegweBBb0hNztKVDsIOsyyZnw+zypngcTU92YNbHg9OO03zIm7qidenSsiWRt2gkFbbGAiXcrJmBd2LIFiv5hLEaRtNtTSsJnKMTTAqWCOeIANLas09HtiuPJsq2hxXSUQsh6rzIc7SGL877X1FXUOrhu7YHFubYj/DynmJda1pwvaUPiBHfu4XTuDNKWG62XdLVuMLguh9XtxbXqMZDj4xxG07dXgYvfVuU32bXU+gPDi0CiUtl96ptUstZKc+1iHpzu92x9TTF15VxKHFOfi5ThQfIzlhURbEpqtM0kOlXBsIzbYnipLABj7MV6qWaEHq54E6rPStfFDjZSmsCTLCg2gmKYW4mnMcRB0nWzPvArmLRVvKgmWhF6UAebwyU3uiBfVTtVRxu0MNNxysuqMzoRxERtgnO9B9Z95WoCWvoRACX5bM1a8aLZUNJThgFdGWKxBea0sWO3IFQ0JaNGwrS5Hhloa0ySYEqi/ZFd11A7NnEcdMCZcgr7KSgTx6nBAURA38AT1brBqJOrk7q1nSThoyaSQxC1ujSOZ8tdhvSrtOkJmwo0W4R1dSfTqb8BEb+pVXieup7iqLPayWQ++kYRdJQaXkfR1sA42UqGCrQS7eSx1uq+0yj5YCrx0zkiajM92JZaUWeoeiGjT1QdGCdqseRElN2qaNHZc53WdKuTjTLooLmNzRpTnbIYNYUzZ+TQfCPCOb9Ypcck7n7GnTIg1Dma1O6XFjox6aBPUaJwbqyMAhtBqCdg+KGS9QKcnsWbO7EnK1PzawRqIJ1yBEvjmbci4LhqmewgnuU+ujofkxtt7t9idPVpuhLzt/j1eJ7FpXtiequjpee7JCFw2VU3MCYmMsavIEA+2PrglFdEIpt6ePczEHHhXXJ5eL53g/6D53a92sgujAOWX9TLiWNCqusD4PJnt4k5awdkIgs6coWCUWnEhya8RNh/MkHk6pS2Nt74tXpVnL0omy/GDrUtjSn8ukf7C1MCtBg3PVkO3eOmy0fXnkFzscwkK9VTRv8PVdHJIS0Oi80E8QvjT0Dd2ai0QWjrslIXkRl4VHRptWkjM7TdUkhESSoWDeVHdXgYnysLRZu6kqqJNxK/IjspML31bkrWbLNKbEy0oOMifRJGl2olG5MqoDj2CnboLNpkJGurwmS0d1C8tr/WBMmH3ZeoGl2wXfqmnbXTVfWi3iylXCiTiFGJA5lcLBd2oSJWqRa8eJu3EXAzbA+IQ/wpvlVlzjPkky7XLBCetJNVWgqaiAFkApcbRR+GGPTtwACraoddRacst28Hq1IA8u60nQmhUX8zirl4FBCrMFvgcyWksI9ZeayIm0N0zjFrbbcLleqNpCU/01OyvIsLBx3ZtVBmgJTWM792uqixMh7FtzbjMzoVxxpr+ZxOoeWpshZEd0L6/xM76JcudANUgaXjM5CsOJSrX5KkvXfAk8Nu7zFTwftrpG00awzMM0dtJOlpEThx2LA8H43hYhCC8mJBSYepaXUSwJmU0sVUrXD9wEw9BN7l4prNnx2JHUT/jyyFpVaMFmTvBMOrP1cG3401Os2nxMMlseT9IIyXwerXCW4TI+vB4DbaaFISgxI33bDdHZw8RisiyXuMEhTb/Nu7pA5WYner3nabaa6hvUk0NtJtiVPJlyh60U9hrTrnzF7oulyXZhX4XuzO+hLt/W/rr2u4rTNE3OcxrONHpQQe+mOE7LDZqkllJLkQSUdydiKJ2M2cGZqp6B4uGJnA3SsmeDjXVsD613tA5he+j1lixaRs6LJM28bFjqKwzxJp5aN3242ZFZT874BQGHRXg+LMzgdA3muVjv6yjIF0qNZUY2SdHUmOHo5rxcgDS2PxS022/hACt8TFqacBELUBBXcmwEaeHQJCfzoMbppTzLi2WGiNJ+WvKT/XbCKWi5CE4osE93sVlESjpgdMedsDVR2jtPZK/72qOngr44aWuuagnQtezl4UgHxmE6abQTT1Hecc6f19wpF1QPOjDL1V4uNjMXPnWaCP7aqbeqTgPFh+gy5qCpV210WFL/9a9/ffhwf1tyoUSaeStuN0bg5z/fX1h9GllpUlZFbVUjY5Q47Sj27Sz1k+qjrNFf3ksl9ujxFqof+dWoTvzb+5+of8eUNk5xfw1lpXEWOZXz5U3Xl1dYX19cvd53BNbL5a1wygxQdi6BYaWmbyQXQOXiFYbtO0n1BNBVxsV8UYraeX7fdQGsvSXZq1EaRWH0T58/f+H1cttWl0+B9bn49bP162vhGNHzZ+jX+84f/Nxe4FkjPxkVRuI5T5QoKJLIX2h2xwi3F1TPP9t521h82ygx8l4UZOb7nS921WfOmxulRvVgPXLcCn8pGyMq8Zeiwm9CRH5iRN5r2dhPD8le3DqKLrFxe6XolG/fBE9w9w1s+vzpr8RePv36qtyBqnegv8J8+gZkAiBA2vYN72n2Ck0fHD3/rzt/7zAJ/vb5s2GZT0b2dBfhCdD/XLxYvz4/P/9Zbz8S/8NPVPUzHVd/IVj9nGB1+wTnbfuxk5R+mvxzeuZf6Jn/fwT8KWwOKCY4sMxJdfv8u4zmVf7WQDh8s4m4jp7u3yuwBzhO6Tzl+PML+LuDpkV1xR/AfuI+jKh7eogJ3OOpeHuznp8/AowP//iZW/y/+cbfPIV3dwbhAP/bcSDtvosEZoD/QTEm/nLH9u4u9p9WA/wleV+rfrBWfd3nuH9DhwD9P9fhvzWj/7so8y4QUN9fmQZiPpbv4fuSGWX5ZqZp9HS3k/8JDH88cz7O5uPne2i/S36/C71i7/ceoeHzx9mv/wU9cAEi2OWWBV7rzDYq5+m3dwnGYAW/PEiV1tWJjfGnsfd1OgL4WDv98xzF9JF9xi9fcHwDuPzVIko/8erIKC6Aqdopx58+Pxy3e/hrd9PUg+Ff/y3C2E/8uI7/hG/86YHtm8jPX7E8pLqpLfVSELAvX1Jc4pTlBejNsapLnWVOMf50V1CdPZT8DcUt990M+JLcR0ouvg348qv+J7vvh/GD3V8i31dhwBffrgHCPyG4m8Tzv9XDPdMUaQvSZhJevs6XjD/djeTdHArzafb8Qzw/VcpfUP3F3n6I710xtlP4zX16Bdhyc8NkRs4/5+6Lot6xPpj9Dss3n3j5gwEb0RdgD1h3eYf4HvoO/Pvzh3tJBZgYAWcDHBuRPzj3mJUZlXV9Suvq023W5fnjf93+ffoAfLh9u43FvNrOTVHgFMqnx2jNq4kit5u28/Rl6OQZOJvvjt5nbl7LqzFfoE8AxfPr1els33PK6un5P96+H3r5VBh+6YykOrmN4DBFkRZPY+c2hmR/mzq6YQS1XRnfuBwDKpXTVW8A8es7B8+/JI5jR85t7OUP/g70ZgFRb/JdXzOjAMp9jUPbL54eF49a5cXp/LK6pOGjcrnXmUCQG5VXKwWsPT3QA95nP2T4nc/vKI6uaRqOkvRecebAUb9wfUdaOFlkWM472pdvRe5k/L+T8eT99gzsuTH+Bs5l+lUpwMBuNW98sxn70kAX/IJdQCh5fMVfs378y13ctvCB5Dd6T7eP518Kp6qL5I7yYQX3UamnZ3DO2duXyalXovDuyPe3qwKoFhSttn0x3m8/jT9+BPwAFY5fAA6jjqq38Tfv9M3i5t5/8rcHazcnBuDl+Ec4b8Hi46MU/g7xHLgedtPdF95f70xewiRtk9v+8un5IUtRJ0+365s0ZWUUQNPgfF5vH0AGwPHbzaTvIK8P/u93/3tr+MW6+pH9OIO7XT3G6y6mYYVOYo9/Ka3Cz6q3n7oU4N5OE+ft28jZ643Zz2VfvjqdY9W3NzTOCzjUpweq55fvdHy7fefgfvcPWrot3eW5B9rHXVDC383sLohlZPeJOYArq6svZfnTXZSysm/iV101fv7eVG6svj4Wn3/5CuoUxc9BwSJAezP+tzun0/F7/LrzBcLd9674ehvFG9/96+Yd96Tsl8Bwopsl/sC53PH3Bj96V/sIHFL19tudhYdt3ALB77+8d33feyIIHLek+QvItGUGstYoSr3yZlPW242XV5BA7fLpzghoveyHbM/Pv3hvtyrhceYPJ758L9d3Ydl69RxgxP8W6Hnkl6P7qXz4O5ntK9J/kgP/SOOnqe5HuP9OXvypCP8uCf6I2N9Mmj+l96M0+SM6/006/Yr/91ucLUvHfvuTPb29QfeKEuTXJ+/1UcE93dJc8fbbGBRCN/HuY6AvY8D/racbf3ofE30Zl9atC7hZ4QUEpAp47KexRvAsTSgg930bEL28D4heHgOil/dswEgKu2IZenxzlQd7IycC3jH+busDlhVAq0LxqsxqzGVFsPyF4kUZbH1UCeNvI7aAhWtVZeWn6dTzq2ttgvwWTzMD4E+z6R/Hgscv4z+Fuk/jx8AxqItBVzG9Df/O8PlH069usN9r9+Z440/32AVuvNc67yAPEkAbv4XvZxY+auHwVgt//mfl9Ms/KZZf/klN/PI3q9+Xv1/n/vr7uyLuVdr4k/cyvlVu3xnK9+Xb48yBHYEaB+STKLUAogyotrAv1hVkuO9D0ArU/87LOI3sCzipx4MlP7kkTvsOa6exAW78dYsXpebNOcCJX6zIAHH369qD2QTEQyBJXvs3HZeVkwFD+PJI7fHc7aHFbnRP/yPQAGfXl9EXPu7P2CIjexllIG7dbGn0MIG7a+3vAoEgbRXpDfdthLy6Asd8ePU7D3fGgI7rxDbuVnyj+gj1APT9od4oTR6P8v4ydP4LyDWjhx6/ELxrZQSs7iH/7VFi5Sf1fZx81DvAokdjB3Bd3mS+7wRH8l1J8fFeZLyz5ySNX6TJLUUBs373EnCC79Pmr48bl/cY8QRS+Zel74Hevzw9/w4CUhVnj5oD1AqXso5jIPc9d76ClfEv4OP7VHxfsOs4K5+KFz+5Gerb/AUYFzjUxEje7uf5fK8un+97v1SgPyQx/lorFl/aBT+514m3cuPF94BDgGD5Xj7+ck/m7zc/ZcXtgYM7/gyyu285v35ZuGV7B3RB4TR0isSJRl+Kv/LT6Ld3mN/vVXLRA0Igwn6t6H554By/jf/HbDb/cumOf7uH3t9HzW/vMff38U9gf6ie569SQjcBis//xhl/fYTe+QdQd1hOVo2Y+7+brRjlyPn0FzK//Tj835q1W4AGoftLiB47tzLncnvuCgwMfD45z68XcGogUF3eVx+h1Hn+/QfMzz98ANx/2fD2Nr5c7p5+GQM13pPY4/TupzT2s/6h//G9/Lo9fABlaJzadeSUd4cce2nqRQ5IDJFh/gjqvUiTe+CuMQPKsKcblecP/wei2AkX"""
# Largest component radius of the frozen v0.9.6 endpoint enclosure, enlarged
# outward to a simple auditable decimal guard.
ENDPOINT_COMPONENT_RADIUS=Decimal("1.3e-15")
getcontext().prec=80

SWITCH=r'''
    # v0.9.10 switch: every subsequent frozen v0.9.3 graph/metric/Picard
    # calculation now uses the corrected centre and the v0.9.9 frame.
    base_phases=theta_b
    whitener=b9
    normal=n9
    tangent=t9
    jacobian0=jc
    _jtmp,gradient0=response_jacobian_and_gradient(theta_b,True)
    jw0=v093_matmul(whitener,jacobian0)
    fb0=v093_matmul(jw0,normal)
    fb_inverse=v093_midpoint_inverse(fb0,"v0.9.10 recentered normal derivative")
'''

def digest(path:Path)->str:
 h=hashlib.sha256();h.update(path.read_bytes());return h.hexdigest()

def locate(explicit:str|None,embedded_destination:Path)->Path:
 candidates=[]
 if explicit:candidates.append(Path(explicit))
 candidates.extend([Path.cwd()/V099,Path("/content")/V099])
 script=globals().get("__file__")
 if script:candidates.append(Path(script).resolve().parent/V099)
 for p in candidates:
  if p.is_file():
   if digest(p)!=V099_SHA:raise RuntimeError(f"v0.9.9 source hash mismatch: {digest(p)}")
   return p.resolve()
 raw=zlib.decompress(base64.b64decode(EMBEDDED_V099_ZLIB_B64))
 if hashlib.sha256(raw).hexdigest()!=V099_SHA:raise RuntimeError("embedded v0.9.9 source hash mismatch")
 embedded_destination.parent.mkdir(parents=True,exist_ok=True)
 embedded_destination.write_bytes(raw)
 return embedded_destination.resolve()

def patch_v099(source:Path,dest:Path)->None:
 text=source.read_text();needle='''    v098_cert.update({'''
 if text.count(needle)!=1:raise RuntimeError("v0.9.9 recentered-frame hook not unique")
 dest.write_text(text.replace(needle,SWITCH+"\n"+needle,1))

def parse():
 p=argparse.ArgumentParser();p.add_argument("--outdir",default="response_fibre_second_chart_v0_9_10_results");p.add_argument("--v099");p.add_argument("--root-radius",default="2e-18")
 return p.parse_known_args()

def run(args):
 start=time.time();out=Path(args.outdir);out.mkdir(parents=True,exist_ok=True);src=locate(args.v099,out/"embedded_backend"/V099);patched=out/"instrumented_v0_9_9_for_v0_9_10.py";patch_v099(src,patched)
 child=out/"formal_recentered_chain";done=subprocess.run([sys.executable,str(patched),"--outdir",str(child),"--root-radius",str(args.root_radius)],text=True,capture_output=True)
 (out/"stdout.txt").write_text(done.stdout);(out/"stderr.txt").write_text(done.stderr)
 frame_summary=child/"run_summary.json"
 picard=child/"v098_formal_backend"/"formal_base"/"intrinsic_picard_microstep_certificate.json"
 rootcert=child/"v098_formal_backend"/"normal_root_arb_certificate.json"
 if not (frame_summary.is_file() and picard.is_file() and rootcert.is_file()):raise RuntimeError(f"instrumented chain exit={done.returncode}; expected certificates missing; inspect logs")
 f=json.loads(frame_summary.read_text());p=json.loads(picard.read_text());c=json.loads(rootcert.read_text())
 inner=Decimal(str(p["inner_real_picard_radius"]));outer=Decimal(str(p["outer_complex_tangent_radius"]));displacement=Decimal(str(p["picard_displacement_upper"]));
 ac=max(abs(Decimal(x)) for x in c["a_c"])
 # Orthogonal old/new frames give a conservative Euclidean-to-sup overlap
 # bound sqrt(6)*component radius; use 2.45 > sqrt(6).
 overlap=Decimal("2.45")*ENDPOINT_COMPONENT_RADIUS+Decimal(str(args.root_radius))
 endpoint_inside=overlap<inner
 next_step_inside=overlap+displacement<inner
 gates={
  "instrumented_chain_exit_zero":done.returncode==0,
  "v098_unique_normal_root":c.get("unique_normal_root_certified") is True,
  "v099_recentered_frame":f.get("all_scientific_gates_pass") is True,
  "new_complex_fibre_graph":p.get("gates",{}).get("complex_parametric_fibre_graph") is True,
  "new_pullback_metric":p.get("gates",{}).get("pullback_metric_positive_definite") is True,
  "new_analytic_normalization_branch":p.get("gates",{}).get("analytic_normalization_branch") is True,
  "new_picard_contraction":p.get("gates",{}).get("picard_contraction") is True,
  "new_picard_self_mapping":p.get("gates",{}).get("picard_self_mapping") is True,
  "new_uniform_strict_L6_descent":p.get("gates",{}).get("uniform_strict_L6_descent") is True,
  "old_endpoint_enclosure_inside_new_inner_domain":endpoint_inside,
  "next_microstep_remains_inside_new_inner_domain":next_step_inside}
 passed=all(gates.values())
 result={"title":TITLE,"version":VERSION,"scientific_status":"VALIDATED_SECOND_LOCAL_FIBRE_CHART_PICARD_MICROSTEP_CERTIFIED" if passed else "SECOND_LOCAL_CHART_INCONCLUSIVE_FAIL_CLOSED",
  "repository":"https://github.com/papasop/Geometric-Flow","formal_backend":"python-flint/Arb 192-bit","source_v099_sha256":V099_SHA,
  "certificates":{"root":str(rootcert),"frame":str(frame_summary),"second_picard":str(picard)},
  "overlap_metrics":{"guarded_old_endpoint_distance_upper":format(overlap,".40E"),"new_inner_radius":str(inner),"new_outer_radius":str(outer),"new_picard_displacement_upper":str(displacement),"maximum_abs_a_c":format(ac,".40E")},
  "picard_metrics":{k:p.get(k) for k in ["complex_graph_krawczyk_utilization","pullback_metric_neumann_defect_upper","intrinsic_field_sup_norm_upper","cauchy_lipschitz_upper","picard_contraction_factor","picard_self_mapping_utilization","uniform_dL6_dt_upper"]},
  "gates":gates,"all_scientific_gates_pass":passed,"second_local_picard_chart_certified":passed,"complete_child_certified":False,"ten_chart_continuation_certified":False,"global_flow_claimed":False,
  "next_required_step":"iterate certified recenter/overlap steps to the child boundary; then certify chart transition inclusion",
  "claim_boundary":"one recentered second local Picard microstep with endpoint inclusion; not complete-child, ten-chart, or global continuation",
  "elapsed_seconds":time.time()-start,"environment":{"python":platform.python_version(),"platform":platform.platform()}}
 tmp=out/"run_summary.json.tmp";tmp.write_text(json.dumps(result,indent=2,allow_nan=False)+"\n");tmp.replace(out/"run_summary.json");return result

def main():
 args,ignored=parse();
 if ignored:print(f"[notice] ignored notebook/kernel arguments: {ignored}")
 try:
  r=run(args);print("="*112);print(f"{TITLE} v{VERSION}");print("="*112);print(json.dumps(r,indent=2));return 0 if r["all_scientific_gates_pass"] else 2
 except Exception as e:print(json.dumps({"scientific_status":"V0910_FAILED_CLOSED","error_type":type(e).__name__,"error":str(e)},indent=2));return 2

if __name__=="__main__":
 code=main()
 if "ipykernel" not in sys.modules and "google.colab" not in sys.modules:raise SystemExit(code)
