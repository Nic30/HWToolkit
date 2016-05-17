from hdl_toolkit.interfaces.std import  BramPort, \
                 BramPort_withoutClk, Ap_hs, Ap_clk, Ap_rst_n, Ap_none, Ap_vld,\
    Ap_rst
from hdl_toolkit.interfaces.amba import Axi4, Axi4_xil, \
    AxiLite, AxiLite_xil, AxiStream, AxiStream_withoutSTRB, AxiStream_withUserAndStrb, AxiStream_withUserAndNoStrb 

allInterfaces = [Axi4, Axi4_xil,
   AxiLite, AxiLite_xil,
   BramPort, BramPort_withoutClk,
   AxiStream_withUserAndStrb, AxiStream, AxiStream_withUserAndNoStrb, AxiStream_withoutSTRB,
   Ap_hs, Ap_clk, Ap_rst, Ap_rst_n, Ap_vld, Ap_none
 ]
