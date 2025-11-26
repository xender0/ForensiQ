

from forensics import PacketCapture
import time

def main():
    print("Starting basic packet capture example...")
    
                             
    capture = PacketCapture(
        interface=None,               
        output_file='example_capture.pcap',
        filter='tcp port 80',                     
        count=100                       
    )
    
                   
    capture.start()
    
                         
    while capture.is_capturing:
        time.sleep(0.5)
    
                    
    stats = capture.get_statistics()
    print("\nCapture Statistics:")
    print(f"Total packets: {stats['total_packets']}")
    print(f"IP packets: {stats.get('ip_packets', 0)}")
    print(f"TCP packets: {stats.get('tcp_packets', 0)}")
    print(f"UDP packets: {stats.get('udp_packets', 0)}")

if __name__ == '__main__':
    main()

