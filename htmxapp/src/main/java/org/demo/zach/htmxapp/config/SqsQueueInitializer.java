package org.demo.zach.htmxapp.config;

import jakarta.annotation.PostConstruct;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import software.amazon.awssdk.services.sqs.SqsClient;
import software.amazon.awssdk.services.sqs.model.CreateQueueRequest;
import software.amazon.awssdk.services.sqs.model.GetQueueUrlRequest;
import software.amazon.awssdk.services.sqs.model.QueueNameExistsException;

@Component
@RequiredArgsConstructor
@Slf4j
public class SqsQueueInitializer {

    private final SqsClient sqsClient;

    @Value("${aws.sqs.queue-name}")
    private String queueName;

    @PostConstruct
    public void createQueueIfMissing() {
        try {
            // Try to fetch queue URL
            GetQueueUrlRequest getReq = GetQueueUrlRequest.builder()
                    .queueName(queueName)
                    .build();

            sqsClient.getQueueUrl(getReq);
            log.info("SQS queue '{}' already exists.", queueName);

        } catch (Exception e) {
            log.warn("SQS queue '{}' not found. Creating it...", queueName);

            try {
                CreateQueueRequest createReq = CreateQueueRequest.builder()
                        .queueName(queueName)
                        .build();

                sqsClient.createQueue(createReq);

                log.info("SQS queue '{}' successfully created.", queueName);

            } catch (QueueNameExistsException exists) {
                log.info("SQS queue '{}' already exists (caught late).", queueName);
            } catch (Exception ex) {
                log.error("Failed to create SQS queue '{}'.", queueName, ex);
            }
        }
    }
}
