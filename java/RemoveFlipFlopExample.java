package com.xilinx.rapidwright.examples;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

import com.xilinx.rapidwright.design.Cell;
import com.xilinx.rapidwright.design.Design;
import com.xilinx.rapidwright.design.Net;
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
        Map<String,String> netReassignments = new HashMap<>();
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
            EDIFNet qNet = output.getNet();
            EDIFNet inputNet = ffInst.getPortInst("D").getNet();
            netReassignments.put(qNet.getName(), inputNet.getName());
            for(EDIFPortInst inst : output.getNet().getPortInsts()) {
            	if(inst.equals(output)) continue;
            	inputNet.addPortInst(inst);
            }
            
            for(EDIFPortInst inst : ffInst.getPortInsts()) {
                inst.getNet().removePortInst(inst);
            }
            ffInst.getParentCell().removeCellInst(ffInst);
            ffInst.getParentCell().removeNet(qNet);
        }
        // Remove site insts
        for(SiteInst siteInst : siteInstsToRemove) {
            design.removeSiteInst(siteInst);
        }
        
        // Replace the Q net with the D net in the physical site routing
        for(SiteInst si : design.getSiteInsts()) {
        	Map<Net,HashSet<String>> netMap = si.getSiteCTags();
        	Map<String,Net> siteWireMap = si.getNetSiteWireMap();
        	for(Net net : new ArrayList<>(netMap.keySet())) {
        		String reassignmentNetName = netReassignments.get(net.getName());
        		if(reassignmentNetName != null) {
        			Net reassignmentNet = design.getNet(reassignmentNetName);
        			HashSet<String> siteWires = si.getSiteCTags().remove(net);
        			si.getNetList().remove(net);
        			si.getNetList().add(reassignmentNet);
        			if(siteWires != null) {
        				si.getSiteCTags().put(reassignmentNet, siteWires);
        			}
        			for(String siteWire : siteWires) {
        				siteWireMap.put(siteWire, reassignmentNet);
        			}
        		}
        	}
        }
        
        t.stop().start("Write DCP");
        design.writeCheckpoint(args[0].replace(".dcp", "_removed_ff.dcp"), CodePerfTracker.SILENT);
        t.stop().printSummary();
    }
}
