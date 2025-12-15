package org.demo.zach.htmxapp.service;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;
import software.amazon.awssdk.services.sqs.SqsClient;
import software.amazon.awssdk.services.sqs.model.DeleteMessageRequest;
import software.amazon.awssdk.services.sqs.model.Message;
import software.amazon.awssdk.services.sqs.model.ReceiveMessageRequest;

import java.util.List;

@Service
@RequiredArgsConstructor
@Slf4j
public class SqsListenerService {

    private final SqsClient sqsClient;

    @Value("${aws.sqs.queue-url}")
    private String queueUrl;

    /**
     * Poll SQS every 5 seconds and log messages.
     */
    @Scheduled(fixedDelay = 5000)
    public void pollMessages() {
        try {
            ReceiveMessageRequest request = ReceiveMessageRequest.builder()
                    .queueUrl(queueUrl)
                    .maxNumberOfMessages(10)
                    .waitTimeSeconds(5)
                    .build();

            List<Message> messages = sqsClient.receiveMessage(request).messages();

            if (messages.isEmpty()) {
                return;
            }

            for (Message msg : messages) {
                // ✅ Log the message body
                log.info("Received SQS message: {}", msg.body());

                // ✅ Optionally log attributes
                if (!msg.messageAttributes().isEmpty()) {
                    log.info("Message attributes: {}", msg.messageAttributes());
                }

                // ✅ Delete message after processing
                deleteMessage(msg);
            }

        } catch (Exception e) {
            log.error("Error while polling SQS messages", e);
        }
    }

    private void deleteMessage(Message msg) {
        DeleteMessageRequest deleteRequest = DeleteMessageRequest.builder()
                .queueUrl(queueUrl)
                .receiptHandle(msg.receiptHandle())
                .build();

        sqsClient.deleteMessage(deleteRequest);
        log.debug("Deleted SQS message with receipt handle: {}", msg.receiptHandle());
    }
}