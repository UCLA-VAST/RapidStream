/*
 * 
 * Copyright (c) 2021 Xilinx, Inc. 
 * All rights reserved.
 *
 * Author: Chris Lavin, Xilinx Research Labs.
 * 
 */
/**
 * 
 */
package com.xilinx.rapidwright.examples;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Map.Entry;
import java.util.Set;
import java.util.Scanner;
import java.io.*;

import com.xilinx.rapidwright.design.Design;
import com.xilinx.rapidwright.design.Net;
import com.xilinx.rapidwright.design.SiteInst;
import com.xilinx.rapidwright.device.PIP;
import com.xilinx.rapidwright.edif.EDIFCell;
import com.xilinx.rapidwright.edif.EDIFCellInst;
import com.xilinx.rapidwright.edif.EDIFNet;
import com.xilinx.rapidwright.edif.EDIFPort;
import com.xilinx.rapidwright.edif.EDIFPortInst;
import com.xilinx.rapidwright.tests.CodePerfTracker;

/**
 * Created on: Jul 12, 2021
 */
public class MergeDCP {

    private static Set<String> cellTypesToSkip; 
    
    static {
        cellTypesToSkip = new HashSet<>();
        cellTypesToSkip.add("VCC");
        cellTypesToSkip.add("GND");
        cellTypesToSkip.add("BUFGCE");
    }
    
    private static EDIFPortInst getOtherPortInst(EDIFPortInst portInst) {
        EDIFNet net = portInst.getNet();
        for(EDIFPortInst otherPortInst : net.getPortInsts()) {
            if(otherPortInst == portInst) continue;
            return otherPortInst;
        }
        return null;
    }
    
    private static void mergeNet(Net dest, Net src) {
        Set<PIP> pips = new HashSet<>(dest.getPIPs());
        pips.addAll(src.getPIPs());
        dest.setPIPs(pips);
    }
    
    private static void removePort(EDIFCell cell, EDIFPort port) {
        // TODO - Move to EDIFCell class
        List<String> portObjectsToRemove = new ArrayList<>();
        for(Entry<String,EDIFPort> p : cell.getPortMap().entrySet()) {
            if(p.getValue() == port || p.getValue().getName().equals(port.getName())) {
                portObjectsToRemove.add(p.getKey());
            }
        }
        for(String s : portObjectsToRemove) {
            cell.getPortMap().remove(s);
        }
    }
    
    public static Design mergeDCP(Design design0, Design design1) {
        // Move logical cells (except anchor register duplicates
        EDIFCell design0Top = design0.getTopEDIFCell();
        EDIFCell design1Top = design1.getTopEDIFCell();
        
        design0.getNetlist().migrateCellAndSubCells(design1Top, true);
        EDIFNet vcc = design0Top.getNet("<const1>");
        EDIFNet gnd = design0Top.getNet("<const0>");
        EDIFNet clk = design0Top.getNet("ap_clk");
        
        // Add cell instances (except duplicates)
        List<String> duplicates = new ArrayList<>();
        for(EDIFCellInst inst : design1Top.getCellInsts()) {
            EDIFCellInst duplicate = design0Top.getCellInst(inst.getName());
            if(duplicate != null) {
                String duplicateName = duplicate.getCellType().getName();
                if(!cellTypesToSkip.contains(duplicateName)) {
                    duplicates.add(inst.getName());
                }
                
            } else {
                design0Top.addCellInst(inst);
                if(inst.getCellType().getName().equals("FDRE")) {
                    gnd.addPortInst(inst.getPortInst("R"));
                    vcc.addPortInst(inst.getPortInst("CE"));
                    clk.addPortInst(inst.getPortInst("C"));
                }else {
                    // slot instance
                    clk.addPortInst(inst.getPortInst(clk.getName()));
                }
            }
        }
        
        // Handle duplicates
        Set<String> netsNotToCopy = new HashSet<>();
        netsNotToCopy.add(vcc.getName());
        netsNotToCopy.add(gnd.getName());
        netsNotToCopy.add(clk.getName());
        netsNotToCopy.add("ap_clk_port");
        Set<String> portsNotToCopy = new HashSet<>();
        portsNotToCopy.add("ap_clk_port");
        for(String duplicate : duplicates) {
            EDIFCellInst anchorRegInst = design0Top.getCellInst(duplicate);
            EDIFPortInst dPort = anchorRegInst.getPortInst("D");
            EDIFPortInst qPort = anchorRegInst.getPortInst("Q");
            EDIFPortInst connectedToD = getOtherPortInst(dPort);
            EDIFPortInst connectedToQ = getOtherPortInst(qPort);
            
            EDIFPortInst topPortInst = connectedToQ.isTopLevelPort() ? connectedToQ : 
                                      (connectedToD.isTopLevelPort() ? connectedToD : null);
            if(topPortInst == null) {
                throw new RuntimeException("ERROR: Duplicate anchor not connected to top level port");
            }
            // Remove top-level port and connect to merged inst instead
            EDIFNet net = topPortInst.getNet();
            net.removePortInst(topPortInst);
            removePort(design0Top, topPortInst.getPort());
            EDIFCellInst design1Anchor = design1Top.getCellInst(duplicate);
            EDIFPortInst design1AnchorQ = design1Anchor.getPortInst("Q");
            EDIFPortInst otherSlotQInput = getOtherPortInst(design1AnchorQ);
            EDIFPortInst design1AnchorD = design1Anchor.getPortInst("D");
            EDIFPortInst otherSlotDInput = getOtherPortInst(design1AnchorD);

            EDIFPortInst slotPortInst = connectedToQ.isTopLevelPort() ? otherSlotQInput : otherSlotDInput;
            net.addPortInst(design0Top.getCellInst(slotPortInst.getCellInst().getName()).getPortInst(slotPortInst.getName()));

            portsNotToCopy.add(topPortInst.getPort().getName());
            netsNotToCopy.add(design1AnchorD.getNet().getName());
            String srcNetName = design1AnchorQ.getNet().getName();
            netsNotToCopy.add(srcNetName);
            Net physNet = design1.getNet(srcNetName);
            if(physNet.hasPIPs()) {
                mergeNet(design0.getNet(net.getName()), physNet);
            }
        }
        
        // Add ports except those connected to duplicates
        for(EDIFPort port : design1Top.getPorts()) {
            if(portsNotToCopy.contains(port.getName())) continue;
            design0Top.addPort(port);
        }
        
        // Add nets except those connected to duplicates
        for(EDIFNet net : design1Top.getNets()) {
            if(netsNotToCopy.contains(net.getName())) continue;
            if(net.getPortInsts().size() == 0) continue;
            design0Top.addNet(net);
        }
        
        // Stitch physical netlist
        for(SiteInst siteInst : design1.getSiteInsts()) {
            if(design0.getSiteInstFromSite(siteInst.getSite()) != null) continue;
            design0.addSiteInst(siteInst);
        }
        
        for(Net net : design1.getNets()) {
            if(netsNotToCopy.contains(net.getName())) continue;
            design0.addNet(net);
        }
        mergeNet(design0.getNet("ap_clk"), design1.getNet("ap_clk"));
        mergeNet(design0.getGndNet(), design1.getGndNet());
        mergeNet(design0.getVccNet(), design1.getVccNet());
        
        // Merge encrypted cells
        List<String> encryptedCells = design1.getNetlist().getEncryptedCells();
        if(encryptedCells != null && encryptedCells.size() > 0) {
            design0.getNetlist().addEncryptedCells(encryptedCells);
        }          

        return design0;
    }
    
    public static void main(String[] args) {
        if(args.length != 2) {
            System.out.println("Usage: <file that contains DCPs> <merged output DCP filename>");
            return;
        }

        CodePerfTracker t = new CodePerfTracker("Merge DCP");
        t.start("Getting target checkpoitns");

        List<String> checkpoints = new ArrayList<String>();
        try {
            // get all DCPs to be merged
            FileInputStream fis = new FileInputStream(args[0]);
            Scanner sc = new Scanner(fis);
            
            while (sc.hasNextLine()) {
                checkpoints.add(sc.nextLine());
            }
        }
        catch (IOException e)   {
            e.printStackTrace(); 
        }


        // loading all checkpoints
        List<Design> designs_list = new ArrayList<Design>();
        for (String dcp : checkpoints) {
            t.stop().start("Read DCP ".concat(dcp));
            Design design = Design.readCheckpoint(dcp, CodePerfTracker.SILENT);
            designs_list.add(design);
        }

        Design[] designs = new Design[designs_list.size()];
        designs = designs_list.toArray(designs);

        // use the first checkpoint as the base
        // add all checkpoitns into the base checkpoint
        Design output = designs[0];
        for (int i = 1; i < designs_list.size(); i++) {
            t.stop().start("Start merging chcekpoint " + i);
            output = mergeDCP(output, designs[i]);
        }
        
        t.stop().start("Write DCP");
        output.writeCheckpoint(args[1], CodePerfTracker.SILENT);
        t.stop().printSummary();
    }
}
