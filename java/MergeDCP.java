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

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Map.Entry;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import java.util.Set;

import com.xilinx.rapidwright.design.Design;
import com.xilinx.rapidwright.design.DesignTools;
import com.xilinx.rapidwright.design.Net;
import com.xilinx.rapidwright.design.NetType;
import com.xilinx.rapidwright.design.SiteInst;
import com.xilinx.rapidwright.device.PIP;
import com.xilinx.rapidwright.edif.EDIFCell;
import com.xilinx.rapidwright.edif.EDIFCellInst;
import com.xilinx.rapidwright.edif.EDIFNet;
import com.xilinx.rapidwright.edif.EDIFPort;
import com.xilinx.rapidwright.edif.EDIFPortInst;
import com.xilinx.rapidwright.edif.EDIFTools;
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
    
    public static Design mergeDCP(Design design0, Design design1) {
        // Move logical cells (except anchor register duplicates
        EDIFCell design0Top = design0.getTopEDIFCell();
        EDIFCell design1Top = design1.getTopEDIFCell();
        
        design0.getNetlist().migrateCellAndSubCells(design1Top, true);
        EDIFNet vcc = EDIFTools.getStaticNet(NetType.VCC, design0Top, design0.getNetlist());
        EDIFNet gnd = EDIFTools.getStaticNet(NetType.GND, design0Top, design0.getNetlist());
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
            design0Top.removePort(topPortInst.getPort());
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
            try{
                design0Top.addNet(net);
            }catch(RuntimeException e) {
                // Check if this is VCC or GND
                List<EDIFPortInst> srcs = net.getSourcePortInsts(false);
                if(srcs != null && srcs.size() >= 1) {
                    EDIFCell cell = srcs.get(0).getCellInst().getCellType(); 
                    if(cell.isPrimitive() && cell.getName().equals("VCC") || cell.getName().equals("GND")) {
                        EDIFNet destNet = design0Top.getNet(net.getName());
                        for(EDIFPortInst portInst : net.getPortInsts()) {
                            destNet.addPortInst(portInst);
                        }
                    }
                }
            }
        }
        
        // Stitch physical netlist
        for(SiteInst siteInst : design1.getSiteInsts()) {
            if(design0.getSiteInstFromSite(siteInst.getSite()) != null) continue;
            design0.addSiteInst(siteInst);
        }
        
        for(Net net : design1.getNets()) {
            if(netsNotToCopy.contains(net.getName())) continue;
            if(net.isStaticNet()) continue;
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

        design0.getNetlist().removeUnusedCellsFromAllWorkLibraries();
        return design0;
    }
    
    public static Design mergeDCP(Design...designs) {
        Design result = null;
        for(Design design : designs) {
            if(result == null) {
                result = design;
            }else {
                result = mergeDCP(result, design);
            }
        }
        
        result.getNetlist().resetParentNetMap();
        DesignTools.makePhysNetNamesConsistent(result);
        return result;
    }
    
    public static void main(String[] args) throws InterruptedException {
        if(args.length != 2 && args.length != 3) {
            System.out.println("Usage: <dir with DCPs> <merged output DCP filename> [dcp regex]");
            return;
        }
        String dcpRegex = args.length == 3 ? args[2] : ".*\\.dcp"; //"^.*CR_X2Y[0-9]+_To_CR_X[0-9]+Y[0-9]+/.*_unique.dcp$"
        CodePerfTracker t = new CodePerfTracker("Merge DCP");
  
        Path start = Paths.get(args[0]);
        List<File> dcps = null;
        try (Stream<Path> stream = Files.walk(start, Integer.MAX_VALUE)) {
            dcps = stream
                    .map(p -> p.toFile())
                    .filter(p -> p.isFile() && p.getAbsolutePath().matches(dcpRegex))
                    .collect(Collectors.toList());
        } catch(IOException e) {
            e.printStackTrace();
        }
        System.out.println("Merging DCPs:");
        for(File f : dcps) {
            System.out.println("  " + f.getAbsolutePath());
        }
        
        Design[] designs = new Design[dcps.size()];
        for(int i=0; i < designs.length; i++) {
            t.start("Read DCP " + i);
            designs[i] = Design.readCheckpoint(dcps.get(i).toPath(), CodePerfTracker.SILENT);
            t.stop();
        }
        
        t.start("Merge DCPs");
        Design merged = mergeDCP(designs);
        t.stop().start("Write DCP");
        merged.writeCheckpoint(args[1], CodePerfTracker.SILENT);
        t.stop().printSummary();
    }
}
