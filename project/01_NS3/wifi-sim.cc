#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/wifi-module.h"
#include "ns3/internet-module.h"
#include "ns3/flow-monitor-module.h"
#include "ns3/mobility-module.h"
#include "ns3/config-store-module.h"
#include "ns3/applications-module.h"

#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <limits>
#include <iomanip>
#include <cmath>

using namespace ns3;

NS_LOG_COMPONENT_DEFINE ("WifiSimulation");

int main (int argc, char *argv[])
{

  // Setup
  double simulationTime = 5; //seconds
  //double interval = 0.1; // was 1.0 second
  uint32_t n = 10;  // number of user
  uint32_t r = 10;  // radius (m)
  bool verbose = false;
  std::string phyMode ("DsssRate11Mbps");

  // Read arguments from command line
  CommandLine cmd;
  cmd.AddValue ("n", "number of users", n);
  cmd.AddValue ("r", "radius", r);
  cmd.AddValue ("scenario", "run particular scenario", scenario);
  cmd.AddValue ("verbose", "turn on log on Wifi component", verbose);
  cmd.Parse (argc, argv);

  // Convert to time object
  //Time interPacketInterval = Seconds (interval);

  // disable fragmentation for frames below 2200 bytes
  Config::SetDefault ("ns3::WifiRemoteStationManager::FragmentationThreshold", StringValue ("2200"));
  // turn off RTS/CTS for frames below 2200 bytes
  Config::SetDefault ("ns3::WifiRemoteStationManager::RtsCtsThreshold", StringValue ("2200"));
  // Fix non-unicast data rate to be the same as that of unicast
  Config::SetDefault ("ns3::WifiRemoteStationManager::NonUnicastMode",
                      StringValue (phyMode));

  NodeContainer apContainer;    // Access Point container
  NodeContainer staContainer;   // Station container
  apContainer.Create (1);
  staContainer.Create (n);

  // The below set of helpers will help us to put together the wifi NICs we want
  WifiHelper wifi;
  if (verbose)
    {
      wifi.EnableLogComponents ();  // Turn on all Wifi logging
    }
  wifi.SetStandard (WIFI_PHY_STANDARD_80211b);

  YansWifiPhyHelper wifiPhy =  YansWifiPhyHelper::Default ();
  wifiPhy.Set ("RxGain", DoubleValue (0) );
  // ns-3 supports RadioTap and Prism tracing extensions for 802.11b
  wifiPhy.SetPcapDataLinkType (YansWifiPhyHelper::DLT_IEEE802_11_RADIO);

  YansWifiChannelHelper wifiChannel;
  wifiChannel.SetPropagationDelay ("ns3::ConstantSpeedPropagationDelayModel");
  wifiChannel.AddPropagationLoss ("ns3::LogDistancePropagationLossModel");

  wifiPhy.SetChannel (wifiChannel.Create ());

  // Add a non-QoS upper mac,
  NqosWifiMacHelper wifiMac = NqosWifiMacHelper::Default ();

  // Setup the rest of the upper mac
  Ssid ssid = Ssid ("wifi-default");
  // setup sta.
  wifiMac.SetType ("ns3::StaWifiMac",
                   "Ssid", SsidValue (ssid),
                   "ActiveProbing", BooleanValue (false));

  // NetDeviceContainer staDevice = wifi.Install (wifiPhy, wifiMac, staContainer);

  // setup ap.
  wifiMac.SetType ("ns3::ApWifiMac",
                   "Ssid", SsidValue (ssid));
  // NetDeviceContainer apDevice = wifi.Install (wifiPhy, wifiMac, apContainer.Get (0));

  // Setup device positions
  MobilityHelper mobility;
  Ptr<ListPositionAllocator> positionAlloc = CreateObject<ListPositionAllocator> ();
  // Circular nodes
  {
    const double PI = 3.141592653589793;
    const double error = 1e-9;
    double theta = 2*PI/n;
    for (uint32_t i = 1; i <= n; i++) {
      double x = r * cos (i * theta);
      double y = r * sin (i * theta);
      if (abs(x) <= error) x = 0;
      if (abs(y) <= error) y = 0;
      //positionAlloc->Add (Vector (x, y, 0.0));
      NS_LOG_UNCOND ("Node-" << i << ":\t x = " << x << "\t y = " << y);
    }
  }
  mobility.SetPositionAllocator (positionAlloc);
  mobility.SetMobilityModel ("ns3::ConstantPositionMobilityModel");
  mobility.Install (staContainer);

  // Setup AP position
  MobilityHelper mobilityAp;
  Ptr<ListPositionAllocator> positionAllocAp = CreateObject<ListPositionAllocator> ();
  positionAllocAp->Add (Vector (0.0, 0.0, 0.0));
  mobilityAp.SetPositionAllocator (positionAllocAp);
  mobilityAp.SetMobilityModel ("ns3::ConstantPositionMobilityModel");
  mobilityAp.Install (apContainer);

  InternetStackHelper internet;
  internet.Install (apContainer);
  internet.Install (staContainer);

  // Assign ipv4 address to the stations
  /*
  Ipv4AddressHelper ipv4;
  NS_LOG_INFO ("Assign IP Addresses.");
  ipv4.SetBase ("10.1.1.0", "255.255.255.0");
  Ipv4InterfaceContainer iAp = ipv4.Assign (apDevice);
  Ipv4InterfaceContainer i = ipv4.Assign (staDevice);
  */

  Simulator::Stop (Seconds (simulationTime));
  Simulator::Run ();
  Simulator::Destroy ();
  return 0;
}
