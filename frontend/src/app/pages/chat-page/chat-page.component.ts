import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { Subscription } from 'rxjs';
import { ChatService, Conversation, Message } from '../../services/chat.service';
import { MessageListComponent } from '../../components/chat/message-list.component';
import { ComposerComponent } from '../../components/chat/composer.component';

@Component({
  selector: 'app-chat-page',
  standalone: true,
  imports: [CommonModule, MessageListComponent, ComposerComponent],
  templateUrl: './chat-page.component.html',
  styleUrls: ['./chat-page.component.scss']
})
export class ChatPageComponent implements OnInit, OnDestroy {
  conversation: Conversation | null = null;
  messages: Message[] = [];
  isTyping = false;
  private subscriptions: Subscription[] = [];

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private chatService: ChatService
  ) {}

  ngOnInit(): void {
    // Subscribe to route params
    const routeSub = this.route.params.subscribe(params => {
      const conversationId = params['id'];
      if (conversationId) {
        this.chatService.setActiveConversation(conversationId);
        this.loadConversation(conversationId);
      } else {
        // No conversation ID - check if there's an active conversation or create one
        this.ensureActiveConversation();
      }
    });
    this.subscriptions.push(routeSub);

    // Subscribe to messages changes
    const msgSub = this.chatService.messages$.subscribe(messages => {
      this.messages = messages;
    });
    this.subscriptions.push(msgSub);

    // Subscribe to active conversation changes
    const activeSub = this.chatService.activeConversation$.subscribe(convId => {
      if (convId) {
        this.loadConversationById(convId);
      }
    });
    this.subscriptions.push(activeSub);
  }

  ngOnDestroy(): void {
    this.subscriptions.forEach(sub => sub.unsubscribe());
  }

  private ensureActiveConversation(): void {
    // Get current active conversation ID
    const activeId = this.chatService.getActiveConversationId();
    
    if (activeId) {
      this.loadConversationById(activeId);
    } else {
      // Create a new conversation
      this.chatService.createConversation().subscribe({
        next: (conv) => {
          this.conversation = conv;
          this.router.navigate(['/app/chat', conv.conversation_id]);
        },
        error: (err) => {
          console.error('Failed to create conversation:', err);
        }
      });
    }
  }

  private loadConversation(conversationId: string): void {
    this.loadConversationById(conversationId);
  }

  private loadConversationById(conversationId: string): void {
    // Find conversation from the conversations list
    this.chatService.conversations$.subscribe(conversations => {
      this.conversation = conversations.find(c => c.conversation_id === conversationId) || null;
    }).unsubscribe();
    
    // Load messages for this conversation
    this.chatService.loadMessages(conversationId);
  }

  async handleSendMessage(content: string): Promise<void> {
    console.log('📨 handleSendMessage called with:', content);
    console.log('📋 Current conversation:', this.conversation);
    
    // If no conversation, create one first
    if (!this.conversation) {
      console.log('🆕 No conversation, creating new one...');
      this.chatService.createConversation().subscribe({
        next: (conv) => {
          this.conversation = conv;
          this.sendMessage(content);
        },
        error: (err) => {
          console.error('Failed to create conversation:', err);
        }
      });
    } else {
      this.sendMessage(content);
    }
  }

  private sendMessage(content: string): void {
    if (!this.conversation) {
      console.error('❌ No conversation available!');
      return;
    }

    this.isTyping = true;

    this.chatService.sendMessage({
      message: content,
      conversation_id: this.conversation.conversation_id
    }).subscribe({
      next: (response) => {
        console.log('✅ Message sent!', response);
        this.isTyping = false;
      },
      error: (err) => {
        console.error('❌ Failed to send message:', err);
        this.isTyping = false;
      }
    });
  }
}
