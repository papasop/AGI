# Step-refinement evidence

Both runs use the same declared arclength
`0.4001624695258889` and the same frozen response-curve input.

| quantity | 80 steps | 160 steps |
| --- | ---: | ---: |
| step size | `0.005002030869073611` | `0.0025010154345368055` |
| total $L_6$ change | `-0.3457666722306385` | `-0.34576661864707603` |
| maximum response gap | `6.750155989720952e-14` | `9.769962616701378e-14` |
| maximum response correction | `1.3037528630831583e-10` | `6.632365435307906e-11` |
| minimum alignment cosine | `0.9999999984107195` | `0.9999999989512591` |
| maximum parallel residual | `5.6378727991905387e-05` | `4.5798272280138687e-05` |
| minimum projected-gradient norm | `0.6410014608815628` | `0.6410166202171632` |

The absolute difference in total $L_6$ change is
`5.35835624759784e-08`.  The relative difference, divided by the magnitude of
the 160-step value, is `1.549703169312337e-7`.

The reconstructed-curve hashes differ because the serialized trajectories
contain different numbers of nodes.  Hash equality is not a convergence
criterion.
