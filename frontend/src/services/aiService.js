import { httpClient } from './httpClient';

export const aiService = {
  async ask({ message, conversationId, coordinates }) {
    const { data } = await httpClient.post('/ai/chat', {
      message,
      conversation_id: conversationId ?? null,
      lat: coordinates.latitude,
      lon: coordinates.longitude,
    });
    return data;
  },

  async listConversations() {
    const { data } = await httpClient.get('/ai/conversations');
    return data;
  },

  async listMessages(conversationId) {
    const { data } = await httpClient.get(`/ai/conversations/${conversationId}/messages`);
    return data;
  },

  async removeConversation(conversationId) {
    await httpClient.delete(`/ai/conversations/${conversationId}`);
  },
};
