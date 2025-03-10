// Copyright (c) 2000-2007, NXP Semiconductor
// Copyright (c) 2007-2014, Delft University of Technology
// Copyright (c) 2015, Auburn University
// All rights reserved, see IP_NOTICE_DISCLAIMER_LICENSE for further information.

// Mextram parameters
`MPIco( LEVEL          ,504            ,""            ,504         ,505         ,"Model level" )
`MPRco( TREF           ,25.0           ,""            ,-273.0      ,inf         ,"Reference temperature" )
`ifdef __XYCE__
    `MPRnb_BOTH( DTA       ,0.0            ,""                                      ,"Difference between the local and global ambient temperatures" )
`else
    `IPRnb( DTA            ,0.0            ,""                                      ,"Difference between the local and global ambient temperatures" )
`endif
aliasparam TRISE = DTA;
aliasparam DTEMP = DTA;
`MPIcc( EXMOD          ,1              ,""            ,0           ,2           ,"Flag for extended modeling of the reverse current gain" )
`MPIcc( EXPHI          ,1              ,""            ,0           ,1           ,"Flag for the distributed high-frequency effects in transient" )
`MPIcc( EXAVL          ,0              ,""            ,0           ,1           ,"Flag for extended modeling of avalanche currents" )

`ifdef SUBSTRATE
`MPIcc( EXSUB          ,0              ,""            ,0           ,1           ,"Flag for extended modelling of substrate currents" )
`endif

`MPRoo( IS             ,22.0a          ,""            ,0.0         ,inf         ,"Collector-emitter saturation current" )
`MPRco( IK             ,0.1            ,""            ,1.0p        ,inf         ,"Collector-emitter high injection knee current" )
`MPRco( VER            ,2.5            ,""            ,0.01        ,inf         ,"Reverse Early voltage" )
`MPRco( VEF            ,44.0           ,""            ,0.01        ,inf         ,"Forward Early voltage" )
`MPRco( BF             ,215.0          ,""            ,0.1m        ,inf         ,"Ideal forward current gain" )
`MPRco( IBF            ,2.7ffff           ,""            ,0.0         ,inf         ,"Saturation current of the non-ideal forward base current" )
`MPRco( MLF            ,2.0            ,""            ,0.1         ,inf         ,"Non-ideality factor of the non-ideal forward base current" )
`MPRco( XIBI           ,0.0            ,""            ,0.0         ,1.0         ,"Part of ideal base current that belongs to the sidewall" )
`MPRco( IZEB           ,0.0            ,""            ,0.0         ,inf         ,"Pre-factor of emitter-base Zener tunneling current" )
`MPRco( NZEB           ,22.0           ,""            ,0.0         ,inf         ,"Coefficient of emitter-base Zener tunneling current" )
`MPRco( BRI            ,7.0            ,""            ,1.0e-4      ,inf         ,"Ideal reverse current gain" )
`MPRco( IBR            ,1.0ffff           ,""            ,0.0         ,inf         ,"Saturation current of the non-ideal reverse base current" )
`MPRnb( VLR            ,0.2            ,""                                      ,"Cross-over voltage of the non-ideal reverse base current" )
`MPRcc( XEXT           ,0.63           ,""            ,0.0         ,1.0         ,"Part of currents and charges that belong to extrinsic region" )
`MPRco( WAVL           ,1.1u           ,""            ,1.0n        ,inf         ,"Epilayer thickness used in weak-avalanche model" )
`MPRco( VAVL           ,3.0            ,""            ,0.01        ,inf         ,"Voltage determining curvature of avalanche current" )
`MPRco( SFH            ,0.3            ,""            ,0.0         ,inf         ,"Current spreading factor of avalanche model when EXAVL=1" )
`MPRco( RE             ,5.0            ,""            ,1.0m        ,inf         ,"Emitter resistance" )
`MPRco( RBC            ,23.0           ,""            ,1.0m        ,inf         ,"Constant part of the base resistance" )
`MPRco( RBV            ,18.0           ,""            ,1.0m        ,inf         ,"Zero-bias value of the variable part of the base resistance" )
`MPRco( RCC            ,12.0           ,""            ,1.0m        ,inf         ,"Constant part of the collector resistance" )
`MPRco( RCV            ,150.0          ,""            ,1.0m        ,inf         ,"Resistance of the un-modulated epilayer" )
`MPRco( SCRCV          ,1250.0         ,""            ,1.0m        ,inf         ,"Space charge resistance of the epilayer" )
`MPRco( IHC            ,4.0m           ,""            ,1.0p        ,inf         ,"Critical current for velocity saturation in the epilayer" )
`MPRco( AXI            ,0.3            ,""            ,0.02        ,inf         ,"Smoothness parameter for the onset of quasi-saturation" )
`MPRco( CJE            ,73.0ffff          ,""            ,0.0         ,inf         ,"Zero-bias emitter-base depletion capacitance" )
`MPRco( VDE            ,0.95           ,""            ,0.05        ,inf         ,"Emitter-base diffusion voltage" )
`MPRco( PE             ,0.4            ,""            ,0.01        ,0.99        ,"Emitter-base grading coefficient" )
`MPRcc( XCJE           ,0.4            ,""            ,0.0         ,1.0         ,"Sidewall fraction of the emitter-base depletion capacitance" )
`MPRco( CBEO           ,0.0            ,""            ,0.0         ,inf         ,"Emitter-base overlap capacitance" )
`MPRco( CJC            ,78.0ffff          ,""            ,0.0         ,inf         ,"Zero-bias collector-base depletion capacitance" )
`MPRco( VDC            ,0.68           ,""            ,0.05        ,inf         ,"Collector-base diffusion voltage" )
`MPRco( PC             ,0.5            ,""            ,0.01        ,0.99        ,"Collector-base grading coefficient" )
`MPRco( XP             ,0.35           ,""            ,0.0         ,0.99        ,"Constant part of Cjc" )
`MPRco( MC             ,0.5            ,""            ,0.0         ,1.0         ,"Coefficient for current modulation of CB depletion capacitance" )
`MPRcc( XCJC           ,32.0m          ,""            ,0.0         ,1.0         ,"Fraction of CB depletion capacitance under the emitter" )
`MPRco( RCBLX          ,0.0            ,""            ,0.0         ,inf         ,"Resistance Collector Buried Layer eXtrinsic" )
`MPRco( RCBLI          ,0.0            ,""            ,0.0         ,inf         ,"Resistance Collector Buried Layer Intrinsic" )
`MPRco( CBCO           ,0.0            ,""            ,0.0         ,inf         ,"Collector-base overlap capacitance" )
`MPRco( MTAU           ,1.0            ,""            ,0.1         ,inf         ,"Non-ideality factor of the emitter stored charge" )
`MPRco( TAUE           ,2.0p           ,""            ,0.0         ,inf         ,"Minimum transit time of stored emitter charge" )
`MPRoo( TAUB           ,4.2p           ,""            ,0.0         ,inf         ,"Transit time of stored base charge" )
`MPRco( TEPI           ,41.0p          ,""            ,0.0         ,inf         ,"Transit time of stored epilayer charge" )
`MPRco( TAUR           ,520.0p         ,""            ,0.0         ,inf         ,"Transit time of reverse extrinsic stored base charge" )
`MPRnb( DEG            ,0.0            ,""                                      ,"Bandgap difference over the base" )
`MPRco( XREC           ,0.0            ,""            ,0.0         ,inf         ,"Pre-factor of the recombination part of Ib1" )
`MPRcc( XQB            ,`one_third     ,""            ,0.0         ,1.0         ,"Emitter-fraction of base diffusion charge" )
`MPRnb( AQBO           ,0.3            ,""                                      ,"Temperature coefficient of the zero-bias base charge" )
`MPRnb( AE             ,0.0            ,""                                      ,"Temperature coefficient of the resistivity of the emitter" )
`MPRnb( AB             ,1.0            ,""                                      ,"Temperature coefficient of the resistivity of the base" )
`MPRnb( AEPI           ,2.5            ,""                                      ,"Temperature coefficient of the resistivity of the epilayer" )
`MPRnb( AEX            ,0.62           ,""                                      ,"Temperature coefficient of the resistivity of the extrinsic base" )
`MPRnb( AC             ,2.0            ,""                                      ,"Temperature coefficient of the resistivity of the collector contact" )
`MPRco( ACBL           ,2.0            ,""            ,0.0         ,inf         ,"Temperature coefficient of the resistivity of the collector buried layer" )
`MPRnb( DVGBF          ,50.0m          ,""                                      ,"Band-gap voltage difference of the forward current gain" )
`MPRnb( DVGBR          ,45.0m          ,""                                      ,"Band-gap voltage difference of the reverse current gain" )
`MPRco( VGB            ,1.17           ,""            ,0.1         ,inf         ,"Band-gap voltage of the base" )
`MPRco( VGC            ,1.18           ,""            ,0.1         ,inf         ,"Band-gap voltage of the collector" )
`MPRco( VGJ            ,1.15           ,""            ,0.1         ,inf         ,"Band-gap voltage recombination emitter-base junction" )
`MPRco( VGZEB          ,1.15           ,""            ,0.1         ,inf         ,"Band-gap voltage at Tref of Zener effect emitter-base junction" )
`MPRoo( AVGEB          ,4.73e-4        ,""            ,-inf        ,inf         ,"Temperature coefficient band-gap voltage for Zener effect emitter-base junction" )
`MPRco( TVGEB          ,636.0          ,""            ,0.0         ,inf         ,"Temperature coefficient band-gap voltage for Zener effect emitter-base junction" )
`MPRnb( DVGTE          ,0.05           ,""                                      ,"Band-gap voltage difference of emitter stored charge" )
`MPRnb( DAIS           ,0.0            ,""                                      ,"Fine tuning of temperature dependence of C-E saturation current" )
`MPRco( AF             ,2.0            ,""            ,0.01        ,inf         ,"Exponent of the Flicker-noise" )
`MPRco( KF             ,20.0p          ,""            ,0.0         ,inf         ,"Flicker-noise coefficient of the ideal base current" )
`MPRco( KFN            ,20.0p          ,""            ,0.0         ,inf         ,"Flicker-noise coefficient of the non-ideal base current" )
`MPIcc( KAVL           ,0              ,""            ,0           ,1           ,"Switch for white noise contribution due to avalanche" )
`MPIcc( KC             ,0              ,""            ,0           ,2           ,"Switch for RF correlation noise model selection" )
`MPRcc( KE             ,0.0            ,""            ,0.0         ,1.0         ,"Fraction of QE in excess phase shift" )
`MPRcc( FTAUN          ,0.0            ,""            ,0.0         ,1.0         ,"Fraction of noise transit time to total transit time" )

`ifdef SUBSTRATE
`MPRco( ISS            ,48.0a          ,""            ,0.0         ,inf         ,"Base-substrate saturation current" )
`MPRoo( ICSS           ,-1.0           ,""            ,-inf        ,inf         ,"Collector-substrate ideal saturation current" )
`MPRco( IKS            ,250.0u         ,""            ,1.0p        ,inf         ,"Base-substrate high injection knee current" )
`MPRco( CJS            ,315.0ffff         ,""            ,0.0         ,inf         ,"Zero-bias collector-substrate depletion capacitance" )
`MPRoo( VDS            ,0.62           ,""            ,0.05        ,inf         ,"Collector-substrate diffusion voltage" )
`MPRoo( PS             ,0.34           ,""            ,0.01        ,0.99        ,"Collector-substrate grading coefficient" )
`MPRco( VGS            ,1.2           ,""            ,0.1         ,inf         ,"Band-gap voltage of the substrate" )
`MPRnb( AS             ,1.58           ,""                                      ,"Substrate temperature coefficient" )
`MPRnb( ASUB           ,2.0            ,""                                      ,"Temperature coefficient for mobility of minorities in the substrate" )
`endif

`ifdef SELFHEATING
`MPRoo( RTH            ,300.0           ,""            ,0.0        ,inf         ,"Thermal resistance" )
`MPRco( CTH            ,3.0nnnn            ,""            ,0.0        ,inf         ,"Thermal capacitance" )
`MPRnb( ATH            ,0.0             ,""                                     ,"Temperature coefficient of the thermal resistance" )
`endif

`MPRoo( MULT           ,1.0             ,""            ,0.0        ,inf         ,"Multiplication factor" )
`MPIty( TYPE           ,1               ,""                                     ,"Flag for NPN (1) or PNP (-1) transistor type" )
`MPRoc( GMIN           ,1.0e-13         ,""            ,0.0        ,1e-10       ,"Minimum conductance" )





