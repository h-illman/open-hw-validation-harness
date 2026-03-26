// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Symbol table implementation internals

#include "Vtop__pch.h"
#include "Vtop.h"
#include "Vtop___024root.h"

// FUNCTIONS
Vtop__Syms::~Vtop__Syms()
{

    // Tear down scope hierarchy
    __Vhier.remove(0, &__Vscope_periph_ctrl);

}

Vtop__Syms::Vtop__Syms(VerilatedContext* contextp, const char* namep, Vtop* modelp)
    : VerilatedSyms{contextp}
    // Setup internal state of the Syms class
    , __Vm_modelp{modelp}
    // Setup module instances
    , TOP{this, namep}
{
        // Check resources
        Verilated::stackCheck(25);
    // Configure time unit / time precision
    _vm_contextp__->timeunit(-9);
    _vm_contextp__->timeprecision(-12);
    // Setup each module's pointers to their submodules
    // Setup each module's pointer back to symbol table (for public functions)
    TOP.__Vconfigure(true);
    // Setup scopes
    __Vscope_TOP.configure(this, name(), "TOP", "TOP", "<null>", 0, VerilatedScope::SCOPE_OTHER);
    __Vscope_periph_ctrl.configure(this, name(), "periph_ctrl", "periph_ctrl", "periph_ctrl", -9, VerilatedScope::SCOPE_MODULE);

    // Set up scope hierarchy
    __Vhier.add(0, &__Vscope_periph_ctrl);

    // Setup export functions
    for (int __Vfinal = 0; __Vfinal < 2; ++__Vfinal) {
        __Vscope_TOP.varInsert(__Vfinal,"addr", &(TOP.addr), false, VLVT_UINT8,VLVD_IN|VLVF_PUB_RW,0,1 ,2,0);
        __Vscope_TOP.varInsert(__Vfinal,"addr_err", &(TOP.addr_err), false, VLVT_UINT8,VLVD_OUT|VLVF_PUB_RW,0,0);
        __Vscope_TOP.varInsert(__Vfinal,"clk", &(TOP.clk), false, VLVT_UINT8,VLVD_IN|VLVF_PUB_RW,0,0);
        __Vscope_TOP.varInsert(__Vfinal,"gpio_out", &(TOP.gpio_out), false, VLVT_UINT8,VLVD_OUT|VLVF_PUB_RW,0,1 ,7,0);
        __Vscope_TOP.varInsert(__Vfinal,"rd_data", &(TOP.rd_data), false, VLVT_UINT8,VLVD_OUT|VLVF_PUB_RW,0,1 ,7,0);
        __Vscope_TOP.varInsert(__Vfinal,"rd_en", &(TOP.rd_en), false, VLVT_UINT8,VLVD_IN|VLVF_PUB_RW,0,0);
        __Vscope_TOP.varInsert(__Vfinal,"rd_valid", &(TOP.rd_valid), false, VLVT_UINT8,VLVD_OUT|VLVF_PUB_RW,0,0);
        __Vscope_TOP.varInsert(__Vfinal,"rst_n", &(TOP.rst_n), false, VLVT_UINT8,VLVD_IN|VLVF_PUB_RW,0,0);
        __Vscope_TOP.varInsert(__Vfinal,"wr_data", &(TOP.wr_data), false, VLVT_UINT8,VLVD_IN|VLVF_PUB_RW,0,1 ,7,0);
        __Vscope_TOP.varInsert(__Vfinal,"wr_en", &(TOP.wr_en), false, VLVT_UINT8,VLVD_IN|VLVF_PUB_RW,0,0);
        __Vscope_periph_ctrl.varInsert(__Vfinal,"ADDR_CTRL", const_cast<void*>(static_cast<const void*>(&(TOP.periph_ctrl__DOT__ADDR_CTRL))), true, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,1 ,2,0);
        __Vscope_periph_ctrl.varInsert(__Vfinal,"ADDR_GPIO", const_cast<void*>(static_cast<const void*>(&(TOP.periph_ctrl__DOT__ADDR_GPIO))), true, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,1 ,2,0);
        __Vscope_periph_ctrl.varInsert(__Vfinal,"ADDR_ID", const_cast<void*>(static_cast<const void*>(&(TOP.periph_ctrl__DOT__ADDR_ID))), true, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,1 ,2,0);
        __Vscope_periph_ctrl.varInsert(__Vfinal,"ADDR_STATUS", const_cast<void*>(static_cast<const void*>(&(TOP.periph_ctrl__DOT__ADDR_STATUS))), true, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,1 ,2,0);
        __Vscope_periph_ctrl.varInsert(__Vfinal,"PERIPHERAL_ID", const_cast<void*>(static_cast<const void*>(&(TOP.periph_ctrl__DOT__PERIPHERAL_ID))), true, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,1 ,7,0);
        __Vscope_periph_ctrl.varInsert(__Vfinal,"addr", &(TOP.periph_ctrl__DOT__addr), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,1 ,2,0);
        __Vscope_periph_ctrl.varInsert(__Vfinal,"addr_err", &(TOP.periph_ctrl__DOT__addr_err), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,0);
        __Vscope_periph_ctrl.varInsert(__Vfinal,"addr_valid", &(TOP.periph_ctrl__DOT__addr_valid), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,0);
        __Vscope_periph_ctrl.varInsert(__Vfinal,"clk", &(TOP.periph_ctrl__DOT__clk), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,0);
        __Vscope_periph_ctrl.varInsert(__Vfinal,"gpio_out", &(TOP.periph_ctrl__DOT__gpio_out), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,1 ,7,0);
        __Vscope_periph_ctrl.varInsert(__Vfinal,"rd_data", &(TOP.periph_ctrl__DOT__rd_data), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,1 ,7,0);
        __Vscope_periph_ctrl.varInsert(__Vfinal,"rd_en", &(TOP.periph_ctrl__DOT__rd_en), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,0);
        __Vscope_periph_ctrl.varInsert(__Vfinal,"rd_valid", &(TOP.periph_ctrl__DOT__rd_valid), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,0);
        __Vscope_periph_ctrl.varInsert(__Vfinal,"reg_ctrl", &(TOP.periph_ctrl__DOT__reg_ctrl), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,1 ,7,0);
        __Vscope_periph_ctrl.varInsert(__Vfinal,"reg_gpio", &(TOP.periph_ctrl__DOT__reg_gpio), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,1 ,7,0);
        __Vscope_periph_ctrl.varInsert(__Vfinal,"reg_status", &(TOP.periph_ctrl__DOT__reg_status), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,1 ,7,0);
        __Vscope_periph_ctrl.varInsert(__Vfinal,"rst_n", &(TOP.periph_ctrl__DOT__rst_n), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,0);
        __Vscope_periph_ctrl.varInsert(__Vfinal,"wr_data", &(TOP.periph_ctrl__DOT__wr_data), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,1 ,7,0);
        __Vscope_periph_ctrl.varInsert(__Vfinal,"wr_en", &(TOP.periph_ctrl__DOT__wr_en), false, VLVT_UINT8,VLVD_NODIR|VLVF_PUB_RW,0,0);
    }
}
