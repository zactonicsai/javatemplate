package org.demo.zach.htmxapp;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.test.util.ReflectionTestUtils;
import software.amazon.awssdk.services.sqs.SqsClient;
import software.amazon.awssdk.services.sqs.model.SendMessageRequest;
import software.amazon.awssdk.services.sqs.model.SendMessageResponse;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

import org.demo.zach.htmxapp.service.SqsSenderService;
import org.junit.jupiter.api.extension.ExtendWith;

@ExtendWith(MockitoExtension.class)
class SqsSenderServiceTest {

    @Mock
    private SqsClient sqsClient;

    private SqsSenderService senderService;

    private final String queueUrl = "http://localstack:4566/000000000000/updates";

    @BeforeEach
    void setUp() {
        senderService = new SqsSenderService(sqsClient);
        // inject @Value field
        ReflectionTestUtils.setField(senderService, "queueUrl", queueUrl);
    }

    @Test
    void sendMessage_shouldSendToQueueAndReturnMessageId() {
        // arrange
        String body = "Hello SQS";
        String expectedMessageId = "1234-abc";

        SendMessageResponse fakeResponse = SendMessageResponse.builder()
                .messageId(expectedMessageId)
                .build();

        when(sqsClient.sendMessage(any(SendMessageRequest.class))).thenReturn(fakeResponse);

        // act
        String messageId = senderService.sendMessage(body);

        // assert
        assertThat(messageId).isEqualTo(expectedMessageId);

        ArgumentCaptor<SendMessageRequest> captor = ArgumentCaptor.forClass(SendMessageRequest.class);
        verify(sqsClient, times(1)).sendMessage(captor.capture());

        SendMessageRequest sentRequest = captor.getValue();
        assertThat(sentRequest.queueUrl()).isEqualTo(queueUrl);
        assertThat(sentRequest.messageBody()).isEqualTo(body);
    }
}
