/**
 * Created by Bill Urrego on 3/31/16.
 */

import org.zeromq.ZContext;
import org.zeromq.ZMQ;
import org.zeromq.ZMsg;

import java.nio.ByteBuffer;
import java.nio.ByteOrder;

public class controller {

    private static int sizeOfInteger = 4;   // bytes

    public static void main(String[] args) {

        // Input argument for sleepTimer and loopcount
        if (args.length != 2) {
            System.out.println("Usage: java -jar controller [hopdelay (msec)] [# of iterations]");
            System.out.println("Usage Example: java -jar controller 10000 10");
            System.exit(0);
        }

        int sleepTimer = Integer.parseInt(args[0]);
        int loopCount = Integer.parseInt(args[1]);

        // Initialize ZMQ and bind to socket
        ZContext context = new ZContext();
        ZMQ.Socket publisher = context.createSocket(ZMQ.PUB);
        publisher.bind("tcp://127.0.0.1:5558");
        System.out.println("[Controller] Started.");

        // controlling frequency ID
        int freqID = 1;
        System.out.println("[Controller] Setting Freq ID = " + Integer.toString(freqID));

        for (int i=0; i<loopCount; i++) {

            // sleep for alittle
            System.out.println("[Controller] Waiting ...");
            try {
                Thread.sleep(sleepTimer);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }

            System.out.println("[Controller] iteration = " + Integer.toString(i));

            // validate Freq ID is within bounds
            if ( (freqID > 3) || (freqID < 1) ) {
                freqID = 1;
                System.out.println(" - - [Controller] Resetting Freq ID = " + Integer.toString(freqID));
            }

            // create ZMQ message
            ZMsg msg = new ZMsg();

            // add integer as byte array[4] to message, specifying byteorder
            msg.add(ByteBuffer.allocate(sizeOfInteger).order(ByteOrder.LITTLE_ENDIAN).putInt((freqID)).array());
            System.out.println(" - - [Controller] ZMQ Message Created.");

            // send message
            msg.send(publisher);
            System.out.println(" - - [Controller] ZMQ Message Sent.");

            // change freqID for next go around
            freqID = freqID + 1;
            System.out.println(" - - [Controller] Requesting Freq ID = " + Integer.toString(freqID));
        }

        System.out.println("[Controller] Finished.");
        publisher.close();
    }
}
