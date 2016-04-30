/* -*-  Mode: C++; c-file-style: "gnu"; indent-tabs-mode:nil; -*- */
/*
 * Copyright (c) 2009 The Boeing Company
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 2 as
 * published by the Free Software Foundation;
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 *
 */

/*
 * NS-3 Project for ET4394 - Wireless Networking course
 * 
 * Author: Andri Rahmadhani
 * Date: April 2016
 * 
 * Reference: Rizqi Hersyandika and Hedi Krishna source code
 *
 */

#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/applications-module.h"
#include "ns3/wifi-module.h"
#include "ns3/mobility-module.h"
#include "ns3/ipv4-global-routing-helper.h"
#include "ns3/internet-module.h"
#include "ns3/flow-monitor-module.h"
#include "ns3/random-waypoint-mobility-model.h"
#include "ns3/random-variable-stream.h"
#include "ns3/config-store-module.h"

#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <limits>
#include <iomanip>
#include <cmath>

using namespace ns3;

NS_LOG_COMPONENT_DEFINE ("Wifi-Simulation-Andri");

int main (int argc, char *argv[])
{

  //------------------------------------------------------------------
  // Setup simulation
  
  // Adding more randomness
  // ======================
  time_t timev;
  time(&timev);
  RngSeedManager::SetSeed(timev);
  RngSeedManager::SetRun (7);
  //==========================

  double simulationTime = 3.0;   // seconds
  bool verbose = false;

  // Parameters
  uint32_t n = 10;  // number of user
  uint32_t r = 10;  // radius (m)
  uint32_t scenario = 0;   // scenario number
  uint32_t payloadSize = 1024;   // payload
  std::string fName ("results.txt");    // default output filename
  std::string phyMode ("DsssRate11Mbps");  // DSSS max data rate
  std::string DataRate ("5Mbps");       // TCP data rate
  //std::string phyMode ("DsssRate5_5Mbps");
  std::string rtsCts ("150");   // rts/cts threshold
  
  // List of scenario
  enum scenarioName {s_static_circular_loc, s_static_random_loc,
    s_dynamic_randomwalk_loc, s_data_rate, s_payload};

  // Read arguments from command line
  CommandLine cmd;
  cmd.AddValue ("n", "number of users", n);
  cmd.AddValue ("r", "radius", r);
  cmd.AddValue ("scenario", "run particular scenario", scenario);
  cmd.AddValue ("verbose", "turn on log on Wifi component", verbose);
  cmd.AddValue ("output", "specifiy output filename", fName);
  cmd.AddValue ("datarate", "specificy TCP datarate traffic",DataRate);
  cmd.AddValue ("dsssdatarate", "specificy DSSS datarate", phyMode);
  cmd.AddValue ("payload", "specificy TCP datarate traffic",payloadSize);
  cmd.AddValue ("rtsCts", "RTS/CTS threshold", rtsCts);
  cmd.Parse (argc, argv);

  // Global configurations
  // =====================
  // disable fragmentation for frames below 2200 bytes
  Config::SetDefault ("ns3::WifiRemoteStationManager::FragmentationThreshold",
                        StringValue ("2200"));
  // turn off RTS/CTS for frames below ’rtsCts’ bytes
  Config::SetDefault ("ns3::WifiRemoteStationManager::RtsCtsThreshold",
                        StringValue (rtsCts));
  // Fix non-unicast data rate to be the same as that of unicast
  Config::SetDefault ("ns3::WifiRemoteStationManager::NonUnicastMode",
                        StringValue (phyMode));

  // Create 1 Access Point (AP)
  NodeContainer apContainer;
  apContainer.Create (1);
  std::cout << "WiFi access point has been created.." << "\n\n";

  // Create client stations
  NodeContainer staContainer;
  staContainer.Create (n);
  std::cout << n << " client nodes has been created.." << "\n\n";

  // -----------------------------------------------------------------
  /* PHY Configuration -- Use YansWifiPhyHelper to configure PHY layer 
     and its interconnection between nodes */
  YansWifiPhyHelper phy = YansWifiPhyHelper::Default ();
  phy.Set ("RxGain", DoubleValue (0) );

  // Channel Helper
  YansWifiChannelHelper channel; 
  channel.SetPropagationDelay ("ns3::ConstantSpeedPropagationDelayModel");
  //channel.AddPropagationLoss ("ns3::FriisPropagationLossModel");
  channel.AddPropagationLoss ("ns3::LogDistancePropagationLossModel");  // Log distance
  //channel.AddPropagationLoss ("ns3::BuildingsPropagationLossModel"); // Presence of building

  phy.SetChannel (channel.Create ());
  
  // Configure Wifi Standard
  WifiHelper wifi = WifiHelper::Default ();
  wifi.SetStandard (WIFI_PHY_STANDARD_80211b);
  std::cout << "Wifi 802.11b, Channel configured.." << "\n\n";
  
  //------------------------------------------------------------------

  /* Data Link Layer configuration */
  // Configure MAC parameter

  // Add a non-QoS upper mac, and disable rate control
  NqosWifiMacHelper mac = NqosWifiMacHelper::Default ();
  wifi.SetRemoteStationManager ("ns3::ConstantRateWifiManager",
                                "DataMode",StringValue (phyMode),
                                "ControlMode",StringValue (phyMode));
  std::cout << "RemoteStationManager configured.." << "\n\n";
    
  // Configure SSID
  Ssid ssid = Ssid ("WiFi-AP-Andri");

  // Set AP MAC
  mac.SetType ("ns3::ApWifiMac",
                     "Ssid", SsidValue (ssid));
  
  // Install phy and mac on AP
  NetDeviceContainer apDevice;
  apDevice = wifi.Install (phy, mac, apContainer);
  
  std::cout << "SSID, ApDevice & StaDevice has been configured.." << "\n\n";  
  
  // Set client MAC    
  mac.SetType ("ns3::StaWifiMac",
                     "Ssid", SsidValue (ssid),
                     "ActiveProbing", BooleanValue (false));

  // Install phy and mac on client device
  NetDeviceContainer staDevices;
  staDevices = wifi.Install (phy, mac, staContainer);
  
  // -----------------------------------------------------------------

  /* Network layer */

  //-------------------------------------------------------------------
  
  // Use mobility helper, select based on scenario
  MobilityHelper mobilitySta, mobilityAp;
  
  // Set nodes locations
  if (scenario == s_static_random_loc)
  {
    ObjectFactory pos;
    char buff[200];
    sprintf(buff,"ns3::UniformRandomVariable[Min=0.0|Max=%f]",float(r));
    pos.SetTypeId ("ns3::RandomDiscPositionAllocator");
    pos.Set ("Theta", StringValue ("ns3::UniformRandomVariable[Min=0.0|Max=6.2830]"));
    pos.Set ("Rho", StringValue (buff));
    Ptr<PositionAllocator> positionAlloc = pos.Create ()->GetObject<PositionAllocator> ();
    mobilitySta.SetPositionAllocator (positionAlloc);
    mobilitySta.SetMobilityModel ("ns3::ConstantPositionMobilityModel");
  }
  else if (scenario == s_dynamic_randomwalk_loc) 
  {
    mobilitySta.SetMobilityModel ("ns3::RandomWalk2dMobilityModel", 
            "Bounds", RectangleValue (Rectangle (-1000, 1000, -1000, 1000)), 
           "Distance", ns3::DoubleValue (300.0)); 
  }  
  else
  {
      // Static circular nodes as default
    Ptr<ListPositionAllocator> positionAlloc = CreateObject<ListPositionAllocator> ();
    {
      const double PI = 3.141592653589793;
      const double error = 1e-9;
      double theta = 2*PI/n;
      for (uint32_t i = 1; i <= n; i++) {
        double x = r * cos (i * theta);
        double y = r * sin (i * theta);
        if (abs(x) <= error) x = 0;
        if (abs(y) <= error) y = 0;
        positionAlloc->Add (Vector (x, y, 0.0));
      }
    }
    mobilitySta.SetPositionAllocator (positionAlloc);
    mobilitySta.SetMobilityModel ("ns3::ConstantPositionMobilityModel");
  }
  mobilitySta.Install (staContainer);

  // Set AP in constant position
  mobilityAp.SetMobilityModel ("ns3::ConstantPositionMobilityModel");
  mobilityAp.Install (apContainer);      
  std::cout << "Mobility has been configured.." << "\n\n";

  // Internet stack
  InternetStackHelper inetStack;
  inetStack.Install (apContainer);
  inetStack.Install (staContainer);

  // configure IPv4 address
  Ipv4AddressHelper address;
  Ipv4Address addr, addrAp;
  address.SetBase ("10.1.1.0", "255.255.255.0");
  Ipv4InterfaceContainer staNodesInterface;
  Ipv4InterfaceContainer apNodeInterface;
  apNodeInterface = address.Assign (apDevice);
  staNodesInterface = address.Assign (staDevices);

  // Display IP address of each node
  for(uint32_t i = 0 ; i < n; i++)
  {
    addr = staNodesInterface.GetAddress(i);
    std::cout << " Node " << i+1 << "\t "<< "IP Address "<<addr << std::endl;
  }
  addrAp = apNodeInterface.GetAddress(0);
  std::cout << " AP IP address " << addrAp << std::endl;
  std::cout << "IPv4 address has been configured.." << "\n\n";

  //----------------------------------------------------------
  /* Transport and Application layer */
  
  // Setting up application
  // Port number for nodes
  uint16_t port[n];
  ApplicationContainer apps[n], sinkApp[n];
  for( uint16_t a = 0; a < n; a = a + 1 )
  {
    port[a]=8000+a;
    Address apLocalAddress (InetSocketAddress (Ipv4Address::GetAny (), port[a]));

    PacketSinkHelper packetSinkHelper ("ns3::TcpSocketFactory",apLocalAddress);
    sinkApp[a] = packetSinkHelper.Install (apContainer.Get (0));
    sinkApp[a].Start (Seconds (0.0));
    sinkApp[a].Stop (Seconds (simulationTime+1));
    
    OnOffHelper onoff ("ns3::TcpSocketFactory",Ipv4Address::GetAny ());
    onoff.SetAttribute ("OnTime", StringValue("ns3::ConstantRandomVariable[Constant=10]"));
    onoff.SetAttribute ("OffTime", StringValue("ns3::ConstantRandomVariable[Constant=0]"));
    onoff.SetAttribute ("PacketSize", UintegerValue (payloadSize));
    onoff.SetAttribute ("DataRate", StringValue (DataRate)); //bit/s

    AddressValue remoteAddress (InetSocketAddress (apNodeInterface.GetAddress (0),port[a]));
    onoff.SetAttribute ("Remote", remoteAddress);
    apps[a].Add (onoff.Install (staContainer.Get (a)));
    apps[a].Start (Seconds (1.0));
    apps[a].Stop (Seconds (simulationTime+1));
  }

  std::cout << "Application is ready to run.." << "\n\n";
  
  // ----------------------------------------------------------------------------------
  /* Measurement */
  // Calculate Throughput using Flowmonitor 
  FlowMonitorHelper flowmon;
  Ptr<FlowMonitor> monitor = flowmon.InstallAll();

  phy.EnablePcap ("wifitcp", apDevice);
  Ipv4GlobalRoutingHelper::PopulateRoutingTables ();


  // Run Simulation
  NS_LOG_INFO ("Run Simulation.");
  Simulator::Stop (Seconds (simulationTime+1));
  Simulator::Run ();

  // Monitoring
  monitor->CheckForLostPackets ();
  double tot=0;
  //double totDelay=0;
  double totsq=0;
  double variance=0;
  
  double throughput[2*n]; // There are 2 flows in TCP for every node
  int psent=0;
  int preceived=0;

  Vector positionNode;    // Position of nodes relative to AP

  Ptr<Ipv4FlowClassifier> classifier = DynamicCast<Ipv4FlowClassifier> (flowmon.GetClassifier ());
  std::map<FlowId, FlowMonitor::FlowStats> stats = monitor->GetFlowStats ();
  
  // prepare output to file
  std::ofstream myFile;
  myFile.open (fName.c_str(),std::ios_base::app);

  myFile << "--- start collecting data ---" << std::endl;
  myFile << "Source Address\t" << "n\t" << "RTS/CTS\t" << "Tx(by)\t" << "Throughput\t" << "Distance\t" << std::endl;
  std::cout << "--- start collecting data ---" << std::endl;
  std::cout << "Source Address\t" << "n\t" << "RTS/CTS\t" << "Tx(by)\t" << "Throughput\t" << "Distance\t" << std::endl;
  for (std::map<FlowId, FlowMonitor::FlowStats>::const_iterator i = stats.begin (); i != stats.end (); ++i)
  {
    Ipv4FlowClassifier::FiveTuple t = classifier->FindFlow (i->first);
    //std::cout << "Flow " << i->first  << " (" << t.sourceAddress << " -> " << t.destinationAddress << ")\t";
    //std::cout << "  Tx Bytes:   " << i->second.txBytes << "\t";
    //std::cout << "  Rx Bytes:   " << i->second.rxBytes << "\t";
    throughput[i->first] = i->second.rxBytes * 8.0 / (i->second.timeLastRxPacket.GetSeconds() - i->second.timeFirstTxPacket.GetSeconds())/1024/1024;
    //std::cout << "  Throughput: " << throughput[i->first]  << " Mbps\n";
    //if (t.destinationAddress=="10.1.1.1")
    if(t.destinationAddress == addrAp)
    {
      int ncount = (i->first)-1;
      Ptr<MobilityModel> mob = staContainer.Get(ncount)->GetObject<MobilityModel>();
      positionNode = mob->GetPosition ();
      std::cout << t.sourceAddress <<"\t";
      std::cout << n << "\t" << rtsCts <<"\t";
      std::cout << i->second.txBytes << "\t";
      std::cout << throughput[i->first]  << "\t";
      std::cout << pow(pow(positionNode.x,2)+pow(positionNode.y,2),0.5) << "\t\n"; // calculate node distance relative to AP
      //std::cout << i->second.delaySum / i->second.rxPackets << "\n";

      myFile << t.sourceAddress << "\t";
      myFile << n << "\t" << rtsCts <<"\t";
      myFile << i->second.txBytes << "\t";
      myFile << throughput[i->first]  << "\t";
      myFile << pow(pow(positionNode.x,2)+pow(positionNode.y,2),0.5) << "\t\n"; // calculate node distance relative to AP

      tot = tot+throughput[i->first];
      totsq = totsq+pow(throughput[i->first],2);
      psent = psent+i->second.txBytes;
      preceived = preceived+i->second.rxBytes;
      //totDelay = totDelay+i->second.delaySum / i->second.rxPackets;

     }
  }
  std::cout << "--- end collecting data ---" << std::endl;
  myFile << "--- end collecting data ---" << std::endl;

  std::cout << "Avg: " << tot/n <<"\n";
  std::cout << "Tot: " << tot <<"\n";
  variance=totsq/n-pow(tot/n,2);
  //std::cout << "Variance: " << variance <<"\t";
  std::cout << "Var: " << pow(variance,0.5)/tot/n <<"\n";
  std::cout << "loss: " << psent-preceived <<"\n";
  std::cout << "sent: " << psent <<"\n";
  //std::cout << "AvgDelay: " << totDelay/n << "\n";
  //std::cout << "TotDelay: " << totDelay <<"\n";

  myFile << "Avg: " << tot/n <<"\n";
  myFile << "Tot: " << tot <<"\n";
  myFile << "Var: " << pow(variance,0.5)/tot/n <<"\n";
  myFile << "loss: " << psent-preceived <<"\n";
  myFile << "sent: " << psent <<"\n";
  
  myFile.close();

  // Close simulator
  Simulator::Destroy ();  
  NS_LOG_INFO ("Done.");
  return 0;
}