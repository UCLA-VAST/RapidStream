package com.xilinx.rapidwright.examples;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import com.xilinx.rapidwright.design.Cell;
import com.xilinx.rapidwright.design.Design;
import com.xilinx.rapidwright.design.SiteInst;
import com.xilinx.rapidwright.edif.EDIFCell;
import com.xilinx.rapidwright.edif.EDIFCellInst;
import com.xilinx.rapidwright.edif.EDIFNet;
import com.xilinx.rapidwright.edif.EDIFPortInst;
import com.xilinx.rapidwright.tests.CodePerfTracker;

public class RemoveFlipFlopExample {
    public static void main(String[] args) {
    	CodePerfTracker t = new CodePerfTracker("Remove Flip Flops");
    	t.start("Read DCP");
        Design design = Design.readCheckpoint(args[0],CodePerfTracker.SILENT);
        t.stop().start("Remove FFs");
        
        // Find cells and site insts to remove (those with FFs)
        Set<SiteInst> siteInstsToRemove = new HashSet<>();
        List<Cell> cellsToRemove = new ArrayList<>();
        for(EDIFCellInst cellInst : design.getNetlist().getTopCell().getCellInsts()) {
        	EDIFCell cellType = cellInst.getCellType();
            if(cellType.isPrimitive() && cellType.getName().equals("FDRE")) {
                Cell cell = design.getCell(cellInst.getName());
                cellsToRemove.add(cell);
                siteInstsToRemove.add(cell.getSiteInst());
            }
        }
        // Remove cells
        for(Cell cell : cellsToRemove) {
        	// Remove physical cell
            design.removeCell(cell);
            // Remove logical cell
            EDIFCellInst ffInst = cell.getEDIFCellInst();
            EDIFPortInst output = ffInst.getPortInst("Q");
            EDIFNet inputNet = ffInst.getPortInst("D").getNet();
            for(EDIFPortInst inst : output.getNet().getPortInsts()) {
            	if(inst.equals(output)) continue;
            	inputNet.addPortInst(inst);
            }

            // disconnect the Q net from both the anchor and the inner module
            // delete the Q net
            EDIFNet outputNet = ffInst.getPortInst("Q").getNet();
            List<EDIFPortInst> portsToRemove = new ArrayList<>();
            for(EDIFPortInst inst : output.getNet().getPortInsts()) {
            	if(inst.equals(output)) continue;
                portsToRemove.add(inst);
            }
            for(EDIFPortInst inst : portsToRemove) {
                outputNet.removePortInst(inst); // disconnect the Q net from the inner module
            } 
            ffInst.getParentCell().removeNet(outputNet); // remove the Q net 
            
            for(EDIFPortInst inst : ffInst.getPortInsts()) {
                inst.getNet().removePortInst(inst);
            }
            ffInst.getParentCell().removeCellInst(ffInst);
        }
        // Remove site insts
        for(SiteInst siteInst : siteInstsToRemove) {
            design.removeSiteInst(siteInst);
        }
        
        t.stop().start("Write DCP");
        design.writeCheckpoint(args[0].replace(".dcp", "_removed_ff.dcp"), CodePerfTracker.SILENT);
        t.stop().printSummary();
    }
}