package org.demo.zach.htmxapp;

import org.demo.zach.htmxapp.service.SqsListenerService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.test.util.ReflectionTestUtils;
import software.amazon.awssdk.services.sqs.SqsClient;
import software.amazon.awssdk.services.sqs.model.*;

import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;
import org.junit.jupiter.api.extension.ExtendWith;

@ExtendWith(MockitoExtension.class)
class SqsListenerServiceTest {

    @Mock
    private SqsClient sqsClient;

    private SqsListenerService listenerService;

    private final String queueUrl = "http://localstack:4566/000000000000/updates";

    @BeforeEach
    void setUp() {
        listenerService = new SqsListenerService(sqsClient);
        ReflectionTestUtils.setField(listenerService, "queueUrl", queueUrl);
    }

    @Test
    void pollMessages_shouldReceiveAndDeleteMessages() {
        // arrange
        Message message1 = Message.builder()
                .body("Test 1")
                .receiptHandle("rh-1")
                .build();

        Message message2 = Message.builder()
                .body("Test 2")
                .receiptHandle("rh-2")
                .build();

        ReceiveMessageResponse response = ReceiveMessageResponse.builder()
                .messages(message1, message2)
                .build();

        when(sqsClient.receiveMessage(any(ReceiveMessageRequest.class))).thenReturn(response);

        // act
        listenerService.pollMessages();

        // assert receive was called
        ArgumentCaptor<ReceiveMessageRequest> receiveCaptor =
                ArgumentCaptor.forClass(ReceiveMessageRequest.class);
        verify(sqsClient, times(1)).receiveMessage(receiveCaptor.capture());

        ReceiveMessageRequest receiveRequest = receiveCaptor.getValue();
        assertThat(receiveRequest.queueUrl()).isEqualTo(queueUrl);

        // assert delete was called for each message
        ArgumentCaptor<DeleteMessageRequest> deleteCaptor =
                ArgumentCaptor.forClass(DeleteMessageRequest.class);
        verify(sqsClient, times(2)).deleteMessage(deleteCaptor.capture());

        List<DeleteMessageRequest> deletes = deleteCaptor.getAllValues();
        assertThat(deletes).extracting(DeleteMessageRequest::receiptHandle)
                .containsExactlyInAnyOrder("rh-1", "rh-2");
    }

    @Test
    void pollMessages_shouldDoNothingWhenNoMessages() {
        ReceiveMessageResponse emptyResponse = ReceiveMessageResponse.builder()
                .messages(List.of())
                .build();

        when(sqsClient.receiveMessage(any(ReceiveMessageRequest.class))).thenReturn(emptyResponse);

        listenerService.pollMessages();

        // no delete calls
        verify(sqsClient, never()).deleteMessage(any(DeleteMessageRequest.class));
    }
}

