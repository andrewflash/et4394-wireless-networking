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

#include <iostream>
#include <fstream>
#include <vector>
#include <string>

// Default Network Topology
//
//   Wifi 802.11b (DSSS 11Mbps)
//
//  o    *    *    *  ...   *
// AP    |    |    |        |
//      n1   n2   n3  ...  nN


using namespace ns3;

NS_LOG_COMPONENT_DEFINE ("RizqiWifi");

int main (int argc, char *argv[])
{
  double StartTime = 0.0;
  double StopTime = 10.0;
  int nNodes = 10;	/*number of node*/
  uint32_t payloadSize = 1472   /*payload*/;
  StringValue DataRate;
  DataRate = StringValue("DsssRate11Mbps");

  CommandLine cmd;
  cmd.Parse (argc,argv);

  	//create access point
	NodeContainer wifiApNode;
  	wifiApNode.Create (1);
  	std::cout << "Access point created.." << '\n';

  	//create nodes
 	NodeContainer wifiStaNodes;
  	wifiStaNodes.Create (nNodes);
	std::cout << "Nodes created.." << '\n';

  	/* The next bit of code constructs the wifi devices and the interconnection
	channel between these wifi nodes. Configure the PHY and channel helpers: */
  	YansWifiPhyHelper phy = YansWifiPhyHelper::Default ();
	phy.Set ("RxGain", DoubleValue (0) );

	YansWifiChannelHelper channel;
 	channel.SetPropagationDelay ("ns3::ConstantSpeedPropagationDelayModel");
  	channel.AddPropagationLoss ("ns3::FriisPropagationLossModel");

  	phy.SetChannel (channel.Create ());

	WifiHelper wifi = WifiHelper::Default ();
	wifi.SetStandard (WIFI_PHY_STANDARD_80211b);
	std::cout << "Wifi 802.11b, Channel configured.." << '\n';

  	// configure MAC parameter
  	wifi.SetRemoteStationManager ("ns3::ConstantRateWifiManager","DataMode", DataRate,
                                      "ControlMode", DataRate);

	// NqosWifiMacHelper object to to work with non-Qos MACs
  	NqosWifiMacHelper mac = NqosWifiMacHelper::Default ();
	std::cout << "RemoteStationManager configured.." << '\n';

	// configure SSID
	Ssid ssid = Ssid ("rizqiWifi");

	mac.SetType ("ns3::StaWifiMac",
               	     "Ssid", SsidValue (ssid),
                     "ActiveProbing", BooleanValue (false));

	NetDeviceContainer staDevices;
	staDevices = wifi.Install (phy, mac, wifiStaNodes);

	mac.SetType ("ns3::ApWifiMac",
               	     "Ssid", SsidValue (ssid));

  	NetDeviceContainer apDevice;
  	apDevice = wifi.Install (phy, mac, wifiApNode);
	std::cout << "SSID, ApDevice & StaDevice configured.." << '\n';

  	// mobility
  	MobilityHelper mobility;

/*	mobility.SetPositionAllocator ("ns3::GridPositionAllocator",
        	                       "MinX", DoubleValue (0.0),
                                       "MinY", DoubleValue (0.0),
                                       "DeltaX", DoubleValue (10.0),
                                       "DeltaY", DoubleValue (10.0),
                                       "GridWidth", UintegerValue (5),
                                       "LayoutType", StringValue ("RowFirst")); */
//  	mobility.SetMobilityModel ("ns3::RandomWaypointMobilityModel", );
  	mobility.SetMobilityModel ("ns3::RandomWalk2dMobilityModel",
                                   "Bounds", RectangleValue (Rectangle (-1000, 1000, -1000, 1000)),
				   "Distance", ns3::DoubleValue (300.0));
  	mobility.Install (wifiStaNodes);

  	mobility.SetMobilityModel ("ns3::ConstantPositionMobilityModel");
  	mobility.Install (wifiApNode);
	std::cout << "Mobility configured.." << '\n';

      	// Internet stack
      	InternetStackHelper stack;
      	stack.Install (wifiApNode);
      	stack.Install (wifiStaNodes);

	// configure IPv4 address
      	Ipv4AddressHelper address;
	Ipv4Address addr;
  	address.SetBase ("10.1.1.0", "255.255.255.0");
      	Ipv4InterfaceContainer staNodesInterface;
      	Ipv4InterfaceContainer apNodeInterface;
      	staNodesInterface = address.Assign (staDevices);
      	apNodeInterface = address.Assign (apDevice);

	for(int i = 0 ; i < nNodes; i++)
	{
	 addr = staNodesInterface.GetAddress(i);
	 std::cout << " Node " << i+1 << "\t "<< "IP Address "<<addr << std::endl;
	}
	addr = apNodeInterface.GetAddress(0);
	std::cout << "IPv4 address configured.." << '\n';

	//setting application
      	ApplicationContainer serverApp;

    	UdpServerHelper myServer (4001);  //port 4001
    	serverApp = myServer.Install (wifiStaNodes.Get (0));
        serverApp.Start (Seconds(StartTime));
        serverApp.Stop (Seconds(StopTime));

        UdpClientHelper myClient (apNodeInterface.GetAddress (0), 4001);  //port 4001
        myClient.SetAttribute ("MaxPackets", UintegerValue (20000));
        myClient.SetAttribute ("Interval", TimeValue (Time ("0.002"))); //packets/s
        myClient.SetAttribute ("PacketSize", UintegerValue (payloadSize));

        ApplicationContainer clientApp = myClient.Install (wifiStaNodes.Get (0));
        clientApp.Start (Seconds(StartTime));
        clientApp.Stop (Seconds(StopTime+5));

	std::cout << "Application ready.." << '\n';

	// Calculate Throughput using Flowmonitor
  	FlowMonitorHelper flowmon;
  	Ptr<FlowMonitor> monitor = flowmon.InstallAll();

  	Simulator::Stop (Seconds(StopTime+2));
  	Simulator::Run ();

  	monitor->CheckForLostPackets ();
  	Ptr<Ipv4FlowClassifier> classifier = DynamicCast<Ipv4FlowClassifier> (flowmon.GetClassifier ());
  	std::map<FlowId, FlowMonitor::FlowStats> stats = monitor->GetFlowStats ();
  	for (std::map<FlowId, FlowMonitor::FlowStats>::const_iterator i = stats.begin (); i != stats.end (); ++i)
    	{
	  Ipv4FlowClassifier::FiveTuple t = classifier->FindFlow (i->first);

          std::cout << "Flow " << i->first  << " (" << t.sourceAddress << " -> " << t.destinationAddress << ")\n";
          std::cout << "  Tx Bytes:   " << i->second.txBytes << "\n";
          std::cout << "  Rx Bytes:   " << i->second.rxBytes << "\n";
      	  std::cout << "  Throughput: " << i->second.rxBytes * 8.0 / (i->second.timeLastRxPacket.GetSeconds() - i->second.timeFirstTxPacket.GetSeconds())/1024  << " kbps\n";
	  std::cout << "  Packet Loss Ratio:   " << i->second.lostPackets / (i->second.rxPackets + i->second.lostPackets) << "\n";
	  std::cout << "  Delay :   " << i->second.delaySum / i->second.rxPackets << "\n";
	  std::cout << "  Jitter :   " << i->second.jitterSum / (i->second.rxPackets - 1) << "\n";
	}

  	Simulator::Destroy ();
  return 0;
}
