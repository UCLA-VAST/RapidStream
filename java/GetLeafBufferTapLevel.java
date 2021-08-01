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

import com.xilinx.rapidwright.device.PIP;
import com.xilinx.rapidwright.device.IntentCode;
import com.xilinx.rapidwright.device.Site;


public class GetRowBufferTapLevel {
  public static void main(String[] args) {
    Design design = Design.readCheckpoint(args[0]);
    Net clk = design.getNet("ap_clk");//the clock net name should be given

    List<Site> sites = new ArrayList<>();

    for(PIP pip : clk.getPIPs()){
      if(pip.getEndNode().getIntentCode() == IntentCode.NODE_GLOBAL_LEAF){
        Site s = pip.getEndNode().getSitePin().getSite();
        if(!sites.contains(s)) sites.add(s);
      }
    }

    //if the tap level of a site has not been set before, it should be 0
    //the possible values of the tapLevel can be set are 1, 2, 4, 8
    for(Site site : sites) {
      try {
        if (site.getName().contains("LEAF")) {
          int tapLevel = clk.getBufferDelay(site);//for setting the tap: clk.setBufferDelay(site)
          System.out.println("site: " + site + ", tap level = " + tapLevel);

          // if (args.length > 1) {
          //   clk.setBufferDelay(site, 1);
          //   System.out.println("set tap level of site " + site + " = 1");
          // }
        }
      }
      catch(Exception e) {}
    }

    if (args.length > 1) {
      design.writeCheckpoint(args[0].replace(".dcp", "_change_tap_level.dcp"));
    }
  }
}