/**
 * Created by Bill Urrego on 3/31/16.
 */

import org.zeromq.ZContext;
import org.zeromq.ZFrame;
import org.zeromq.ZMQ;
import org.zeromq.ZMsg;

import java.nio.ByteBuffer;
import java.nio.ByteOrder;

public class testReceiveCommand {

    public static void main(String[] args) {

        // Initialize ZMQ and bind to socket
        ZContext context = new ZContext();
        ZMQ.Socket subscriber = context.createSocket(ZMQ.SUB);
        subscriber.connect("tcp://127.0.0.1:5558");
        System.out.println("[Test Subscriber] Started.");

        // Subscribe to null topic name
        subscriber.subscribe("".getBytes());

        while(!Thread.currentThread().isInterrupted())
        {
            // Wait for message
            ZMsg msg = ZMsg.recvMsg(subscriber);
            if (msg != null)
            {
                System.out.println("[Test Subscriber] Received Command.");
                ZFrame frame = msg.getFirst();

                // Look at frame, get bytes
                if (frame != null) {

                    byte[] bytes = frame.getData();
                    int freqID = ByteBuffer.wrap(bytes).order(ByteOrder.LITTLE_ENDIAN).getInt();
                    System.out.println(" - - [Test Subscriber] Set Freq ID =  " + Integer.toString(freqID));
                }
                else
                    System.out.println(" - - [Test Subscriber] Frame is Null.");
            }
            else
                System.out.println(" - - [Test Subscriber] Msg is Null.");
        }

        subscriber.close();
    }
}
