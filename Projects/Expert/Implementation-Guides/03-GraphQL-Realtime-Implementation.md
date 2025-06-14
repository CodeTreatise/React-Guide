# 🔄 GraphQL Real-time Collaboration Platform Implementation Guide

> **Project**: Advanced GraphQL Real-time Collaboration Platform  
> **Level**: Expert  
> **Estimated Time**: 10-15 hours  
> **Focus**: GraphQL architecture, real-time subscriptions, operational transforms, advanced caching

---

## 🚀 Quick Start (45 minutes)

### Step 1: Setup Monorepo Project
```bash
mkdir graphql-collaboration-platform
cd graphql-collaboration-platform

# Initialize monorepo with Lerna
npx lerna init --independent
npm install

# Setup packages
mkdir -p packages/client packages/server packages/shared

# Client setup
cd packages/client
npx create-react-app . --template typescript
npm install @apollo/client graphql apollo-server-express subscriptions-transport-ws
npm install @types/node

# Server setup  
cd ../server
npm init -y
npm install apollo-server-express graphql graphql-subscriptions express
npm install mongoose redis ioredis jsonwebtoken bcryptjs
npm install -D @types/node typescript ts-node nodemon

# Shared package
cd ../shared
npm init -y
npm install typescript
```

### Step 2: Quick GraphQL Schema
```typescript
// packages/server/src/schema/typeDefs.ts
import { gql } from 'apollo-server-express';

export const typeDefs = gql`
  type Document {
    id: ID!
    title: String!
    content: String!
    version: Int!
    collaborators: [User!]!
    operations: [Operation!]!
    createdAt: String!
    updatedAt: String!
  }

  type Operation {
    id: ID!
    type: OperationType!
    position: Int!
    content: String
    authorId: ID!
    timestamp: String!
    documentId: ID!
  }

  enum OperationType {
    INSERT
    DELETE
    RETAIN
  }

  type User {
    id: ID!
    name: String!
    email: String!
    avatar: String
    presence: Presence
  }

  type Presence {
    userId: ID!
    documentId: ID!
    cursor: Int
    selection: Selection
    lastSeen: String!
  }

  type Selection {
    start: Int!
    end: Int!
  }

  type Query {
    documents: [Document!]!
    document(id: ID!): Document
    users: [User!]!
  }

  type Mutation {
    createDocument(input: CreateDocumentInput!): Document!
    applyOperation(input: OperationInput!): OperationResult!
    updatePresence(input: PresenceInput!): Presence!
  }

  type Subscription {
    operationAdded(documentId: ID!): Operation!
    presenceUpdated(documentId: ID!): Presence!
    documentUpdated(documentId: ID!): Document!
  }

  input CreateDocumentInput {
    title: String!
    content: String
  }

  input OperationInput {
    type: OperationType!
    position: Int!
    content: String
    documentId: ID!
  }

  input PresenceInput {
    documentId: ID!
    cursor: Int
    selection: SelectionInput
  }

  input SelectionInput {
    start: Int!
    end: Int!
  }

  type OperationResult {
    success: Boolean!
    operation: Operation
    error: String
  }
`;
```

### Step 3: Quick Client Setup
```typescript
// packages/client/src/apollo/client.ts
import { ApolloClient, InMemoryCache, createHttpLink, split } from '@apollo/client';
import { getMainDefinition } from '@apollo/client/utilities';
import { WebSocketLink } from '@apollo/client/link/ws';

const httpLink = createHttpLink({
  uri: 'http://localhost:4000/graphql',
});

const wsLink = new WebSocketLink({
  uri: 'ws://localhost:4000/graphql',
  options: {
    reconnect: true,
  },
});

const splitLink = split(
  ({ query }) => {
    const definition = getMainDefinition(query);
    return (
      definition.kind === 'OperationDefinition' &&
      definition.operation === 'subscription'
    );
  },
  wsLink,
  httpLink,
);

export const client = new ApolloClient({
  link: splitLink,
  cache: new InMemoryCache({
    typePolicies: {
      Document: {
        fields: {
          operations: {
            merge: (existing = [], incoming) => [...existing, ...incoming],
          },
        },
      },
    },
  }),
});
```

### Step 4: Basic Collaborative Editor
```typescript
// packages/client/src/components/CollaborativeEditor.tsx
import React, { useState, useEffect, useRef } from 'react';
import { useQuery, useMutation, useSubscription } from '@apollo/client';
import { GET_DOCUMENT, APPLY_OPERATION, OPERATION_ADDED } from '../graphql/operations';

interface CollaborativeEditorProps {
  documentId: string;
}

export const CollaborativeEditor: React.FC<CollaborativeEditorProps> = ({ documentId }) => {
  const [content, setContent] = useState('');
  const [cursor, setCursor] = useState(0);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  
  const { data, loading } = useQuery(GET_DOCUMENT, {
    variables: { id: documentId },
  });

  const [applyOperation] = useMutation(APPLY_OPERATION);

  useSubscription(OPERATION_ADDED, {
    variables: { documentId },
    onSubscriptionData: ({ subscriptionData }) => {
      const operation = subscriptionData.data?.operationAdded;
      if (operation) {
        applyRemoteOperation(operation);
      }
    },
  });

  useEffect(() => {
    if (data?.document) {
      setContent(data.document.content);
    }
  }, [data]);

  const handleTextChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newContent = e.target.value;
    const oldContent = content;
    
    // Calculate operation
    const operation = calculateOperation(oldContent, newContent, cursor);
    
    setContent(newContent);
    
    // Send operation to server
    if (operation) {
      applyOperation({
        variables: {
          input: {
            ...operation,
            documentId,
          },
        },
      });
    }
  };

  const calculateOperation = (oldText: string, newText: string, cursorPos: number) => {
    // Simple diff for demo - production would use more sophisticated algorithm
    if (newText.length > oldText.length) {
      return {
        type: 'INSERT',
        position: cursorPos,
        content: newText.slice(cursorPos, cursorPos + (newText.length - oldText.length)),
      };
    } else if (newText.length < oldText.length) {
      return {
        type: 'DELETE',
        position: cursorPos,
        content: null,
      };
    }
    return null;
  };

  const applyRemoteOperation = (operation: any) => {
    // Apply remote operation to local content
    setContent(current => {
      if (operation.type === 'INSERT') {
        return current.slice(0, operation.position) + 
               operation.content + 
               current.slice(operation.position);
      } else if (operation.type === 'DELETE') {
        return current.slice(0, operation.position) + 
               current.slice(operation.position + 1);
      }
      return current;
    });
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div className="collaborative-editor">
      <h2>{data?.document?.title}</h2>
      <textarea
        ref={textareaRef}
        value={content}
        onChange={handleTextChange}
        onSelect={(e) => setCursor(e.currentTarget.selectionStart)}
        className="editor-textarea"
        placeholder="Start typing to collaborate..."
      />
      <div className="editor-stats">
        Version: {data?.document?.version} | 
        Collaborators: {data?.document?.collaborators?.length || 0}
      </div>
    </div>
  );
};
```

---

## 📖 Complete Implementation Guide

### Phase 1: Advanced GraphQL Server Architecture

#### 1.1 Server Setup with Apollo Server
```typescript
{% raw %}
{% raw %}
// packages/server/src/index.ts
import express from 'express';
import { ApolloServer } from 'apollo-server-express';
import { createServer } from 'http';
import { SubscriptionServer } from 'subscriptions-transport-ws';
import { execute, subscribe } from 'graphql';
import { makeExecutableSchema } from '@graphql-tools/schema';
import mongoose from 'mongoose';
import { typeDefs } from './schema/typeDefs';
import { resolvers } from './schema/resolvers';
import { context } from './context';

async function startServer() {
  // Connect to MongoDB
  await mongoose.connect(process.env.MONGODB_URI || 'mongodb://localhost:27017/collaboration');
  
  const app = express();
  const httpServer = createServer(app);
  
  const schema = makeExecutableSchema({
    typeDefs,
    resolvers,
  });

  const server = new ApolloServer({
    schema,
    context,
    plugins: [
      {
        serverWillStart() {
          return {
            drainServer() {
              subscriptionServer.close();
            },
          };
        },
      },
    ],
  });

  const subscriptionServer = SubscriptionServer.create(
    {
      schema,
      execute,
      subscribe,
      context,
    },
    {
      server: httpServer,
      path: '/graphql',
    }
  );

  await server.start();
  server.applyMiddleware({ app });

  const PORT = process.env.PORT || 4000;
  httpServer.listen(PORT, () => {
    console.log(`🚀 Server ready at http://localhost:${PORT}${server.graphqlPath}`);
    console.log(`🚀 Subscriptions ready at ws://localhost:${PORT}${server.graphqlPath}`);
  });
}

startServer().catch(error => {
  console.error('Failed to start server:', error);
});
{% endraw %}
{% endraw %}
```

#### 1.2 MongoDB Models
```typescript
// packages/server/src/models/Document.ts
import mongoose, { Schema, Document as MongoDocument } from 'mongoose';

export interface IDocument extends MongoDocument {
  title: string;
  content: string;
  version: number;
  collaborators: string[];
  operations: string[];
  createdBy: string;
  createdAt: Date;
  updatedAt: Date;
}

const DocumentSchema = new Schema<IDocument>({
  title: { type: String, required: true },
  content: { type: String, default: '' },
  version: { type: Number, default: 0 },
  collaborators: [{ type: Schema.Types.ObjectId, ref: 'User' }],
  operations: [{ type: Schema.Types.ObjectId, ref: 'Operation' }],
  createdBy: { type: Schema.Types.ObjectId, ref: 'User', required: true },
}, {
  timestamps: true,
});

export const DocumentModel = mongoose.model<IDocument>('Document', DocumentSchema);

// packages/server/src/models/Operation.ts
import mongoose, { Schema, Document as MongoDocument } from 'mongoose';

export interface IOperation extends MongoDocument {
  type: 'INSERT' | 'DELETE' | 'RETAIN';
  position: number;
  content?: string;
  authorId: string;
  documentId: string;
  version: number;
  timestamp: Date;
}

const OperationSchema = new Schema<IOperation>({
  type: { type: String, enum: ['INSERT', 'DELETE', 'RETAIN'], required: true },
  position: { type: Number, required: true },
  content: { type: String },
  authorId: { type: Schema.Types.ObjectId, ref: 'User', required: true },
  documentId: { type: Schema.Types.ObjectId, ref: 'Document', required: true },
  version: { type: Number, required: true },
  timestamp: { type: Date, default: Date.now },
});

export const OperationModel = mongoose.model<IOperation>('Operation', OperationSchema);

// packages/server/src/models/User.ts
import mongoose, { Schema, Document as MongoDocument } from 'mongoose';

export interface IUser extends MongoDocument {
  name: string;
  email: string;
  avatar?: string;
  lastSeen: Date;
}

const UserSchema = new Schema<IUser>({
  name: { type: String, required: true },
  email: { type: String, required: true, unique: true },
  avatar: { type: String },
  lastSeen: { type: Date, default: Date.now },
});

export const UserModel = mongoose.model<IUser>('User', UserSchema);
```

#### 1.3 Advanced Resolvers with Operational Transform
```typescript
// packages/server/src/schema/resolvers.ts
import { PubSub, withFilter } from 'graphql-subscriptions';
import { DocumentModel } from '../models/Document';
import { OperationModel } from '../models/Operation';
import { UserModel } from '../models/User';
import { OperationalTransform } from '../utils/operationalTransform';
import { RedisService } from '../services/RedisService';

const pubsub = new PubSub();

export const resolvers = {
  Query: {
    documents: async (_, __, { user }) => {
      return DocumentModel.find({ 
        collaborators: user.id 
      }).populate('collaborators').sort({ updatedAt: -1 });
    },

    document: async (_, { id }, { user }) => {
      const doc = await DocumentModel.findById(id).populate('collaborators');
      if (!doc || !doc.collaborators.some(c => c.id === user.id)) {
        throw new Error('Document not found or access denied');
      }
      return doc;
    },
  },

  Mutation: {
    createDocument: async (_, { input }, { user }) => {
      const document = new DocumentModel({
        ...input,
        createdBy: user.id,
        collaborators: [user.id],
      });
      
      await document.save();
      return document.populate('collaborators');
    },

    applyOperation: async (_, { input }, { user }) => {
      const { documentId, type, position, content } = input;
      
      try {
        // Get current document version
        const document = await DocumentModel.findById(documentId);
        if (!document) {
          throw new Error('Document not found');
        }

        // Check access permission
        if (!document.collaborators.includes(user.id)) {
          throw new Error('Access denied');
        }

        // Get pending operations for this document
        const pendingOps = await RedisService.getPendingOperations(documentId);
        
        // Create operation object
        const operation = {
          type,
          position,
          content,
          authorId: user.id,
          documentId,
          version: document.version + 1,
          timestamp: new Date(),
        };

        // Transform operation against pending operations
        let transformedOperation = operation;
        for (const pendingOp of pendingOps) {
          if (pendingOp.authorId !== user.id) {
            transformedOperation = OperationalTransform.transform(
              transformedOperation,
              pendingOp
            );
          }
        }

        // Apply operation to document content
        const newContent = OperationalTransform.apply(
          document.content,
          transformedOperation
        );

        // Update document
        document.content = newContent;
        document.version += 1;
        await document.save();

        // Save operation
        const savedOperation = new OperationModel(transformedOperation);
        await savedOperation.save();

        // Add to document operations
        document.operations.push(savedOperation.id);
        await document.save();

        // Cache operation temporarily
        await RedisService.cacheOperation(documentId, savedOperation);

        // Publish to subscribers
        pubsub.publish('OPERATION_ADDED', {
          operationAdded: savedOperation,
          documentId,
        });

        pubsub.publish('DOCUMENT_UPDATED', {
          documentUpdated: document,
          documentId,
        });

        return {
          success: true,
          operation: savedOperation,
        };

      } catch (error) {
        console.error('Apply operation error:', error);
        return {
          success: false,
          error: error.message,
        };
      }
    },

    updatePresence: async (_, { input }, { user }) => {
      const presence = {
        userId: user.id,
        documentId: input.documentId,
        cursor: input.cursor,
        selection: input.selection,
        lastSeen: new Date(),
      };

      // Cache presence in Redis
      await RedisService.cachePresence(input.documentId, user.id, presence);

      // Publish to subscribers
      pubsub.publish('PRESENCE_UPDATED', {
        presenceUpdated: presence,
        documentId: input.documentId,
      });

      return presence;
    },
  },

  Subscription: {
    operationAdded: {
      subscribe: withFilter(
        () => pubsub.asyncIterator(['OPERATION_ADDED']),
        (payload, variables) => {
          return payload.documentId === variables.documentId;
        }
      ),
    },

    presenceUpdated: {
      subscribe: withFilter(
        () => pubsub.asyncIterator(['PRESENCE_UPDATED']),
        (payload, variables) => {
          return payload.documentId === variables.documentId;
        }
      ),
    },

    documentUpdated: {
      subscribe: withFilter(
        () => pubsub.asyncIterator(['DOCUMENT_UPDATED']),
        (payload, variables) => {
          return payload.documentId === variables.documentId;
        }
      ),
    },
  },

  // Resolvers for nested fields
  Document: {
    collaborators: async (document) => {
      return UserModel.find({ _id: { $in: document.collaborators } });
    },
    operations: async (document) => {
      return OperationModel.find({ _id: { $in: document.operations } })
        .sort({ timestamp: 1 });
    },
  },
};
```

#### 1.4 Operational Transform Implementation
```typescript
// packages/server/src/utils/operationalTransform.ts
export interface Operation {
  type: 'INSERT' | 'DELETE' | 'RETAIN';
  position: number;
  content?: string;
  authorId: string;
  version: number;
}

export class OperationalTransform {
  /**
   * Transform two concurrent operations
   */
  static transform(op1: Operation, op2: Operation): Operation {
    if (op1.type === 'INSERT' && op2.type === 'INSERT') {
      return this.transformInsertInsert(op1, op2);
    } else if (op1.type === 'INSERT' && op2.type === 'DELETE') {
      return this.transformInsertDelete(op1, op2);
    } else if (op1.type === 'DELETE' && op2.type === 'INSERT') {
      return this.transformDeleteInsert(op1, op2);
    } else if (op1.type === 'DELETE' && op2.type === 'DELETE') {
      return this.transformDeleteDelete(op1, op2);
    }
    
    return op1; // No transformation needed
  }

  private static transformInsertInsert(op1: Operation, op2: Operation): Operation {
    if (op1.position <= op2.position) {
      return op1; // No change needed
    } else {
      return {
        ...op1,
        position: op1.position + (op2.content?.length || 0),
      };
    }
  }

  private static transformInsertDelete(op1: Operation, op2: Operation): Operation {
    if (op1.position <= op2.position) {
      return op1; // No change needed
    } else {
      return {
        ...op1,
        position: op1.position - 1, // Adjust for deleted character
      };
    }
  }

  private static transformDeleteInsert(op1: Operation, op2: Operation): Operation {
    if (op1.position < op2.position) {
      return op1; // No change needed
    } else {
      return {
        ...op1,
        position: op1.position + (op2.content?.length || 0),
      };
    }
  }

  private static transformDeleteDelete(op1: Operation, op2: Operation): Operation {
    if (op1.position < op2.position) {
      return op1; // No change needed
    } else if (op1.position > op2.position) {
      return {
        ...op1,
        position: op1.position - 1,
      };
    } else {
      // Same position - one of them becomes a no-op
      return {
        ...op1,
        type: 'RETAIN',
      };
    }
  }

  /**
   * Apply operation to text content
   */
  static apply(content: string, operation: Operation): string {
    switch (operation.type) {
      case 'INSERT':
        return content.slice(0, operation.position) + 
               (operation.content || '') + 
               content.slice(operation.position);
      
      case 'DELETE':
        return content.slice(0, operation.position) + 
               content.slice(operation.position + 1);
      
      case 'RETAIN':
        return content; // No change
      
      default:
        return content;
    }
  }

  /**
   * Compose multiple operations into a single operation
   */
  static compose(ops: Operation[]): Operation[] {
    // Implementation for composing operations
    // This is a simplified version - production would be more complex
    return ops.reduce((composed, op) => {
      const lastOp = composed[composed.length - 1];
      
      if (lastOp && this.canCompose(lastOp, op)) {
        composed[composed.length - 1] = this.composeOperations(lastOp, op);
      } else {
        composed.push(op);
      }
      
      return composed;
    }, [] as Operation[]);
  }

  private static canCompose(op1: Operation, op2: Operation): boolean {
    return op1.authorId === op2.authorId &&
           op1.type === op2.type &&
           Math.abs(op1.position - op2.position) <= 1;
  }

  private static composeOperations(op1: Operation, op2: Operation): Operation {
    if (op1.type === 'INSERT' && op2.type === 'INSERT') {
      return {
        ...op1,
        content: (op1.content || '') + (op2.content || ''),
      };
    }
    // Add more composition rules as needed
    return op2;
  }
}
```

### Phase 2: Advanced Client Implementation

#### 2.1 Apollo Client with Advanced Caching
```typescript
{% raw %}
{% raw %}
// packages/client/src/apollo/client.ts
import {
  ApolloClient,
  InMemoryCache,
  createHttpLink,
  split,
  from,
} from '@apollo/client';
import { setContext } from '@apollo/client/link/context';
import { onError } from '@apollo/client/link/error';
import { getMainDefinition } from '@apollo/client/utilities';
import { WebSocketLink } from '@apollo/client/link/ws';
import { RetryLink } from '@apollo/client/link/retry';

// HTTP Link
const httpLink = createHttpLink({
  uri: process.env.REACT_APP_GRAPHQL_HTTP_URI || 'http://localhost:4000/graphql',
});

// WebSocket Link for subscriptions
const wsLink = new WebSocketLink({
  uri: process.env.REACT_APP_GRAPHQL_WS_URI || 'ws://localhost:4000/graphql',
  options: {
    reconnect: true,
    connectionParams: () => ({
      authorization: localStorage.getItem('token'),
    }),
  },
});

// Auth Link
const authLink = setContext((_, { headers }) => {
  const token = localStorage.getItem('token');
  return {
    headers: {
      ...headers,
      authorization: token ? `Bearer ${token}` : '',
    },
  };
});

// Error Link
const errorLink = onError(({ graphQLErrors, networkError, operation, forward }) => {
  if (graphQLErrors) {
    graphQLErrors.forEach(({ message, locations, path }) => {
      console.error(
        `GraphQL error: Message: ${message}, Location: ${locations}, Path: ${path}`
      );
    });
  }

  if (networkError) {
    console.error(`Network error: ${networkError}`);
    // Handle specific network errors
    if (networkError.statusCode === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
  }
});

// Retry Link
const retryLink = new RetryLink({
  delay: {
    initial: 300,
    max: Infinity,
    jitter: true,
  },
  attempts: {
    max: 3,
    retryIf: (error, _operation) => !!error,
  },
});

// Split link for HTTP and WebSocket
const splitLink = split(
  ({ query }) => {
    const definition = getMainDefinition(query);
    return (
      definition.kind === 'OperationDefinition' &&
      definition.operation === 'subscription'
    );
  },
  wsLink,
  from([retryLink, authLink, errorLink, httpLink])
);

// Cache configuration
const cache = new InMemoryCache({
  typePolicies: {
    Document: {
      fields: {
        operations: {
          merge: (existing = [], incoming, { args, readField }) => {
            // Merge operations chronologically
            const merged = [...existing];
            
            incoming.forEach((incomingOp: any) => {
              const exists = existing.find((existingOp: any) => 
                readField('id', existingOp) === readField('id', incomingOp)
              );
              
              if (!exists) {
                merged.push(incomingOp);
              }
            });
            
            // Sort by timestamp
            return merged.sort((a, b) => {
              const aTime = readField('timestamp', a);
              const bTime = readField('timestamp', b);
              return new Date(aTime).getTime() - new Date(bTime).getTime();
            });
          },
        },
        collaborators: {
          merge: (existing = [], incoming) => {
            // Simple merge for collaborators
            return incoming;
          },
        },
      },
    },
    Query: {
      fields: {
        documents: {
          merge: (existing = [], incoming) => {
            // Merge documents list
            return incoming;
          },
        },
      },
    },
  },
});

export const client = new ApolloClient({
  link: splitLink,
  cache,
  defaultOptions: {
    watchQuery: {
      errorPolicy: 'all',
    },
    query: {
      errorPolicy: 'all',
    },
  },
});
{% endraw %}
{% endraw %}
```

#### 2.2 Advanced Collaborative Editor
```typescript
{% raw %}
{% raw %}
// packages/client/src/components/CollaborativeEditor.tsx
import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useQuery, useMutation, useSubscription } from '@apollo/client';
import { debounce } from 'lodash';
import {
  GET_DOCUMENT,
  APPLY_OPERATION,
  UPDATE_PRESENCE,
  OPERATION_ADDED,
  PRESENCE_UPDATED,
  DOCUMENT_UPDATED,
} from '../graphql/operations';
import { OperationalTransform } from '../utils/operationalTransform';
import { PresenceIndicator } from './PresenceIndicator';
import { CommentSystem } from './CommentSystem';
import { VersionHistory } from './VersionHistory';

interface CollaborativeEditorProps {
  documentId: string;
  userId: string;
}

export const CollaborativeEditor: React.FC<CollaborativeEditorProps> = ({
  documentId,
  userId,
}) => {
  const [content, setContent] = useState('');
  const [localOperations, setLocalOperations] = useState<any[]>([]);
  const [cursor, setCursor] = useState(0);
  const [selection, setSelection] = useState({ start: 0, end: 0 });
  const [collaborators, setCollaborators] = useState<any[]>([]);
  const [showComments, setShowComments] = useState(false);
  const [showHistory, setShowHistory] = useState(false);

  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const operationQueueRef = useRef<any[]>([]);
  const lastVersionRef = useRef(0);

  // GraphQL operations
  const { data, loading, error } = useQuery(GET_DOCUMENT, {
    variables: { id: documentId },
    fetchPolicy: 'cache-and-network',
  });

  const [applyOperation] = useMutation(APPLY_OPERATION, {
    onCompleted: (data) => {
      if (data.applyOperation.success) {
        // Remove completed operation from queue
        const operationId = data.applyOperation.operation.id;
        operationQueueRef.current = operationQueueRef.current.filter(
          op => op.tempId !== operationId
        );
      }
    },
    onError: (error) => {
      console.error('Operation failed:', error);
      // Handle conflict resolution
      resolveConflict(error);
    },
  });

  const [updatePresence] = useMutation(UPDATE_PRESENCE);

  // Subscriptions
  useSubscription(OPERATION_ADDED, {
    variables: { documentId },
    onSubscriptionData: ({ subscriptionData }) => {
      const operation = subscriptionData.data?.operationAdded;
      if (operation && operation.authorId !== userId) {
        handleRemoteOperation(operation);
      }
    },
  });

  useSubscription(PRESENCE_UPDATED, {
    variables: { documentId },
    onSubscriptionData: ({ subscriptionData }) => {
      const presence = subscriptionData.data?.presenceUpdated;
      if (presence && presence.userId !== userId) {
        updateCollaboratorPresence(presence);
      }
    },
  });

  useSubscription(DOCUMENT_UPDATED, {
    variables: { documentId },
    onSubscriptionData: ({ subscriptionData }) => {
      const document = subscriptionData.data?.documentUpdated;
      if (document) {
        lastVersionRef.current = document.version;
      }
    },
  });

  // Initialize content
  useEffect(() => {
    if (data?.document) {
      setContent(data.document.content);
      lastVersionRef.current = data.document.version;
    }
  }, [data]);

  // Handle remote operations
  const handleRemoteOperation = useCallback((remoteOperation: any) => {
    setContent(currentContent => {
      let transformedOperation = remoteOperation;
      
      // Transform against pending local operations
      for (const localOp of operationQueueRef.current) {
        transformedOperation = OperationalTransform.transform(
          transformedOperation,
          localOp
        );
      }
      
      // Apply transformed operation
      return OperationalTransform.apply(currentContent, transformedOperation);
    });

    // Update cursor position if needed
    if (remoteOperation.position <= cursor) {
      if (remoteOperation.type === 'INSERT') {
        setCursor(prev => prev + (remoteOperation.content?.length || 0));
      } else if (remoteOperation.type === 'DELETE') {
        setCursor(prev => Math.max(0, prev - 1));
      }
    }
  }, [cursor]);

  // Handle text changes
  const handleTextChange = useCallback((e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newContent = e.target.value;
    const oldContent = content;
    const cursorPosition = e.target.selectionStart;
    
    // Calculate operation
    const operation = calculateOperation(oldContent, newContent, cursorPosition);
    
    if (operation) {
      // Add temporary ID for tracking
      const operationWithId = {
        ...operation,
        tempId: `temp-${Date.now()}-${Math.random()}`,
        authorId: userId,
        documentId,
      };
      
      // Add to local operations queue
      operationQueueRef.current.push(operationWithId);
      
      // Update local content immediately (optimistic update)
      setContent(newContent);
      setCursor(cursorPosition);
      
      // Send to server
      applyOperation({
        variables: {
          input: {
            type: operation.type,
            position: operation.position,
            content: operation.content,
            documentId,
          },
        },
        optimisticResponse: {
          applyOperation: {
            __typename: 'OperationResult',
            success: true,
            operation: {
              __typename: 'Operation',
              id: operationWithId.tempId,
              ...operationWithId,
              timestamp: new Date().toISOString(),
            },
          },
        },
      });
    }
  }, [content, userId, documentId, applyOperation]);

  // Calculate operation between two text states
  const calculateOperation = (oldText: string, newText: string, cursorPos: number) => {
    const oldLength = oldText.length;
    const newLength = newText.length;
    
    if (newLength > oldLength) {
      // Text was inserted
      const insertedText = newText.slice(cursorPos - (newLength - oldLength), cursorPos);
      return {
        type: 'INSERT' as const,
        position: cursorPos - (newLength - oldLength),
        content: insertedText,
      };
    } else if (newLength < oldLength) {
      // Text was deleted
      return {
        type: 'DELETE' as const,
        position: cursorPos,
        content: null,
      };
    }
    
    return null;
  };

  // Update presence (debounced)
  const debouncedUpdatePresence = useCallback(
    debounce((cursor: number, selection: { start: number; end: number }) => {
      updatePresence({
        variables: {
          input: {
            documentId,
            cursor,
            selection,
          },
        },
      });
    }, 100),
    [documentId, updatePresence]
  );

  // Handle cursor/selection changes
  const handleSelectionChange = useCallback((e: React.SyntheticEvent<HTMLTextAreaElement>) => {
    const target = e.target as HTMLTextAreaElement;
    const newCursor = target.selectionStart;
    const newSelection = {
      start: target.selectionStart,
      end: target.selectionEnd,
    };
    
    setCursor(newCursor);
    setSelection(newSelection);
    
    debouncedUpdatePresence(newCursor, newSelection);
  }, [debouncedUpdatePresence]);

  // Update collaborator presence
  const updateCollaboratorPresence = useCallback((presence: any) => {
    setCollaborators(prev => {
      const filtered = prev.filter(c => c.userId !== presence.userId);
      return [...filtered, presence];
    });
  }, []);

  // Conflict resolution
  const resolveConflict = useCallback((error: any) => {
    console.warn('Conflict detected, resyncing...', error);
    // In a real implementation, you would:
    // 1. Fetch the latest document state
    // 2. Replay local operations
    // 3. Resolve conflicts using operational transform
    window.location.reload(); // Simple resolution for demo
  }, []);

  if (loading) return <div className="loading">Loading document...</div>;
  if (error) return <div className="error">Error loading document: {error.message}</div>;

  return (
    <div className="collaborative-editor">
      <div className="editor-header">
        <h1>{data?.document?.title}</h1>
        <div className="editor-controls">
          <button onClick={() => setShowComments(!showComments)}>
            Comments {showComments ? '🔽' : '▶️'}
          </button>
          <button onClick={() => setShowHistory(!showHistory)}>
            History {showHistory ? '🔽' : '▶️'}
          </button>
          <div className="version-info">
            Version: {lastVersionRef.current}
          </div>
        </div>
      </div>

      <div className="editor-body">
        <div className="editor-main">
          <div className="editor-container">
            <textarea
              ref={textareaRef}
              value={content}
              onChange={handleTextChange}
              onSelect={handleSelectionChange}
              className="editor-textarea"
              placeholder="Start typing to collaborate in real-time..."
              spellCheck={false}
            />
            
            {/* Render collaborator cursors */}
            {collaborators.map(collaborator => (
              <PresenceIndicator
                key={collaborator.userId}
                presence={collaborator}
                textareaRef={textareaRef}
              />
            ))}
          </div>

          <div className="collaborators-list">
            <h3>Collaborators ({data?.document?.collaborators?.length || 0})</h3>
            {data?.document?.collaborators?.map((collaborator: any) => (
              <div key={collaborator.id} className="collaborator-item">
                <img 
                  src={collaborator.avatar || '/default-avatar.png'} 
                  alt={collaborator.name}
                  className="collaborator-avatar"
                />
                <span>{collaborator.name}</span>
                {collaborators.find(c => c.userId === collaborator.id) && (
                  <span className="online-indicator">🟢</span>
                )}
              </div>
            ))}
          </div>
        </div>

        {showComments && (
          <div className="editor-sidebar">
            <CommentSystem documentId={documentId} />
          </div>
        )}

        {showHistory && (
          <div className="editor-sidebar">
            <VersionHistory documentId={documentId} />
          </div>
        )}
      </div>
    </div>
  );
};
{% endraw %}
{% endraw %}
```

#### 2.3 Real-time Presence System
```typescript
{% raw %}
{% raw %}
// packages/client/src/components/PresenceIndicator.tsx
import React, { useEffect, useState } from 'react';

interface PresenceIndicatorProps {
  presence: {
    userId: string;
    user?: {
      name: string;
      avatar?: string;
    };
    cursor: number;
    selection?: {
      start: number;
      end: number;
    };
  };
  textareaRef: React.RefObject<HTMLTextAreaElement>;
}

export const PresenceIndicator: React.FC<PresenceIndicatorProps> = ({
  presence,
  textareaRef,
}) => {
  const [position, setPosition] = useState({ top: 0, left: 0 });
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    if (!textareaRef.current || presence.cursor === undefined) return;

    const textarea = textareaRef.current;
    const text = textarea.value;
    
    // Calculate cursor position in pixels
    const cursorPosition = calculateCursorPosition(textarea, presence.cursor);
    
    if (cursorPosition) {
      setPosition(cursorPosition);
      setIsVisible(true);
      
      // Hide after 3 seconds of inactivity
      const timer = setTimeout(() => setIsVisible(false), 3000);
      return () => clearTimeout(timer);
    }
  }, [presence.cursor, textareaRef]);

  const calculateCursorPosition = (textarea: HTMLTextAreaElement, cursorIndex: number) => {
    // Create a temporary div to measure text
    const div = document.createElement('div');
    const style = window.getComputedStyle(textarea);
    
    // Copy textarea styles to div
    div.style.font = style.font;
    div.style.fontSize = style.fontSize;
    div.style.fontFamily = style.fontFamily;
    div.style.lineHeight = style.lineHeight;
    div.style.padding = style.padding;
    div.style.border = style.border;
    div.style.whiteSpace = 'pre-wrap';
    div.style.wordWrap = 'break-word';
    div.style.position = 'absolute';
    div.style.visibility = 'hidden';
    div.style.width = `${textarea.clientWidth}px`;
    
    document.body.appendChild(div);
    
    // Get text up to cursor position
    const textToCursor = textarea.value.substring(0, cursorIndex);
    div.textContent = textToCursor;
    
    // Add a span at the cursor position
    const span = document.createElement('span');
    span.textContent = '|';
    div.appendChild(span);
    
    const rect = span.getBoundingClientRect();
    const textareaRect = textarea.getBoundingClientRect();
    
    document.body.removeChild(div);
    
    return {
      top: rect.top - textareaRect.top + textarea.scrollTop,
      left: rect.left - textareaRect.left + textarea.scrollLeft,
    };
  };

  if (!isVisible) return null;

  return (
    <div
      className="presence-indicator"
      style={{
        position: 'absolute',
        top: position.top,
        left: position.left,
        zIndex: 1000,
      }}
    >
      <div className="cursor-line" />
      <div className="user-info">
        {presence.user?.avatar && (
          <img src={presence.user.avatar} alt="" className="user-avatar" />
        )}
        <span className="user-name">{presence.user?.name || 'Anonymous'}</span>
      </div>
    </div>
  );
};
{% endraw %}
{% endraw %}
```

### Phase 3: Advanced Features

#### 3.1 Comment System
```typescript
// packages/client/src/components/CommentSystem.tsx
import React, { useState } from 'react';
import { useQuery, useMutation, useSubscription } from '@apollo/client';
import {
  GET_COMMENTS,
  ADD_COMMENT,
  COMMENT_ADDED,
  RESOLVE_COMMENT,
} from '../graphql/comments';

interface CommentSystemProps {
  documentId: string;
}

export const CommentSystem: React.FC<CommentSystemProps> = ({ documentId }) => {
  const [newComment, setNewComment] = useState('');
  const [selectedRange, setSelectedRange] = useState<{ start: number; end: number } | null>(null);

  const { data, loading } = useQuery(GET_COMMENTS, {
    variables: { documentId },
  });

  const [addComment] = useMutation(ADD_COMMENT, {
    refetchQueries: [GET_COMMENTS],
  });

  const [resolveComment] = useMutation(RESOLVE_COMMENT, {
    refetchQueries: [GET_COMMENTS],
  });

  useSubscription(COMMENT_ADDED, {
    variables: { documentId },
    onSubscriptionData: ({ subscriptionData, client }) => {
      const newComment = subscriptionData.data?.commentAdded;
      if (newComment) {
        // Update cache
        const existingData = client.readQuery({
          query: GET_COMMENTS,
          variables: { documentId },
        });
        
        if (existingData) {
          client.writeQuery({
            query: GET_COMMENTS,
            variables: { documentId },
            data: {
              comments: [...existingData.comments, newComment],
            },
          });
        }
      }
    },
  });

  const handleAddComment = async () => {
    if (!newComment.trim()) return;

    await addComment({
      variables: {
        input: {
          documentId,
          content: newComment,
          range: selectedRange,
        },
      },
    });

    setNewComment('');
    setSelectedRange(null);
  };

  const handleResolveComment = async (commentId: string) => {
    await resolveComment({
      variables: { id: commentId },
    });
  };

  if (loading) return <div>Loading comments...</div>;

  return (
    <div className="comment-system">
      <h3>Comments</h3>
      
      <div className="add-comment">
        <textarea
          value={newComment}
          onChange={(e) => setNewComment(e.target.value)}
          placeholder="Add a comment..."
          className="comment-input"
        />
        <button onClick={handleAddComment} disabled={!newComment.trim()}>
          Add Comment
        </button>
      </div>

      <div className="comments-list">
        {data?.comments
          ?.filter((comment: any) => !comment.resolved)
          .map((comment: any) => (
            <div key={comment.id} className="comment-item">
              <div className="comment-header">
                <img 
                  src={comment.author.avatar || '/default-avatar.png'}
                  alt={comment.author.name}
                  className="comment-avatar"
                />
                <span className="comment-author">{comment.author.name}</span>
                <span className="comment-time">
                  {new Date(comment.createdAt).toLocaleString()}
                </span>
              </div>
              
              <div className="comment-content">{comment.content}</div>
              
              {comment.range && (
                <div className="comment-range">
                  On text: "{comment.range.text}"
                </div>
              )}
              
              <div className="comment-actions">
                <button onClick={() => handleResolveComment(comment.id)}>
                  Resolve
                </button>
              </div>
            </div>
          ))}
      </div>
    </div>
  );
};
```

#### 3.2 Version History
```typescript
{% raw %}
{% raw %}
// packages/client/src/components/VersionHistory.tsx
import React, { useState } from 'react';
import { useQuery, useMutation } from '@apollo/client';
import { GET_DOCUMENT_VERSIONS, RESTORE_VERSION } from '../graphql/versions';

interface VersionHistoryProps {
  documentId: string;
}

export const VersionHistory: React.FC<VersionHistoryProps> = ({ documentId }) => {
  const [selectedVersion, setSelectedVersion] = useState<number | null>(null);
  const [showDiff, setShowDiff] = useState(false);

  const { data, loading } = useQuery(GET_DOCUMENT_VERSIONS, {
    variables: { id: documentId },
  });

  const [restoreVersion] = useMutation(RESTORE_VERSION, {
    refetchQueries: ['GetDocument'],
  });

  const handleRestoreVersion = async (version: number) => {
    if (window.confirm(`Restore to version ${version}? This will create a new version.`)) {
      await restoreVersion({
        variables: {
          documentId,
          version,
        },
      });
    }
  };

  const calculateDiff = (oldContent: string, newContent: string) => {
    // Simple diff calculation - in production, use a proper diff library
    const oldLines = oldContent.split('\n');
    const newLines = newContent.split('\n');
    
    const diff = [];
    const maxLines = Math.max(oldLines.length, newLines.length);
    
    for (let i = 0; i < maxLines; i++) {
      const oldLine = oldLines[i] || '';
      const newLine = newLines[i] || '';
      
      if (oldLine !== newLine) {
        if (oldLine && newLine) {
          diff.push({ type: 'modified', old: oldLine, new: newLine, line: i + 1 });
        } else if (oldLine) {
          diff.push({ type: 'deleted', content: oldLine, line: i + 1 });
        } else {
          diff.push({ type: 'added', content: newLine, line: i + 1 });
        }
      }
    }
    
    return diff;
  };

  if (loading) return <div>Loading version history...</div>;

  const versions = data?.document?.versions || [];

  return (
    <div className="version-history">
      <h3>Version History</h3>
      
      <div className="version-controls">
        <label>
          <input
            type="checkbox"
            checked={showDiff}
            onChange={(e) => setShowDiff(e.target.checked)}
          />
          Show differences
        </label>
      </div>

      <div className="versions-list">
        {versions.map((version: any, index: number) => (
          <div
            key={version.id}
            className={`version-item ${selectedVersion === version.number ? 'selected' : ''}`}
            onClick={() => setSelectedVersion(
              selectedVersion === version.number ? null : version.number
            )}
          >
            <div className="version-header">
              <span className="version-number">Version {version.number}</span>
              <span className="version-time">
                {new Date(version.createdAt).toLocaleString()}
              </span>
              <span className="version-author">{version.author.name}</span>
            </div>
            
            {version.description && (
              <div className="version-description">{version.description}</div>
            )}
            
            <div className="version-stats">
              {version.operations.length} operations
            </div>
            
            {selectedVersion === version.number && (
              <div className="version-details">
                <div className="version-actions">
                  <button onClick={() => handleRestoreVersion(version.number)}>
                    Restore This Version
                  </button>
                </div>
                
                {showDiff && index < versions.length - 1 && (
                  <div className="version-diff">
                    <h4>Changes from previous version:</h4>
                    {calculateDiff(
                      versions[index + 1].content,
                      version.content
                    ).map((change, idx) => (
                      <div key={idx} className={`diff-line diff-${change.type}`}>
                        <span className="line-number">{change.line}</span>
                        {change.type === 'modified' ? (
                          <>
                            <div className="diff-old">- {change.old}</div>
                            <div className="diff-new">+ {change.new}</div>
                          </>
                        ) : (
                          <div className={`diff-${change.type}`}>
                            {change.type === 'added' ? '+' : '-'} {change.content}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
{% endraw %}
{% endraw %}
```

### Phase 4: Performance Optimization

#### 4.1 Redis Caching Service
```typescript
{% raw %}
{% raw %}
// packages/server/src/services/RedisService.ts
import Redis from 'ioredis';

export class RedisService {
  private static client = new Redis(process.env.REDIS_URL || 'redis://localhost:6379');

  static async cacheOperation(documentId: string, operation: any) {
    const key = `pending_ops:${documentId}`;
    await this.client.lpush(key, JSON.stringify(operation));
    await this.client.expire(key, 300); // 5 minutes TTL
  }

  static async getPendingOperations(documentId: string) {
    const key = `pending_ops:${documentId}`;
    const operations = await this.client.lrange(key, 0, -1);
    return operations.map(op => JSON.parse(op));
  }

  static async cachePresence(documentId: string, userId: string, presence: any) {
    const key = `presence:${documentId}:${userId}`;
    await this.client.setex(key, 60, JSON.stringify(presence)); // 1 minute TTL
  }

  static async getDocumentPresence(documentId: string) {
    const pattern = `presence:${documentId}:*`;
    const keys = await this.client.keys(pattern);
    const presences = await Promise.all(
      keys.map(async key => {
        const data = await this.client.get(key);
        return data ? JSON.parse(data) : null;
      })
    );
    return presences.filter(Boolean);
  }

  static async cacheDocument(documentId: string, document: any) {
    const key = `document:${documentId}`;
    await this.client.setex(key, 300, JSON.stringify(document)); // 5 minutes TTL
  }

  static async getCachedDocument(documentId: string) {
    const key = `document:${documentId}`;
    const data = await this.client.get(key);
    return data ? JSON.parse(data) : null;
  }

  static async invalidateDocument(documentId: string) {
    const keys = [
      `document:${documentId}`,
      `pending_ops:${documentId}`,
    ];
    await this.client.del(...keys);
  }
}
{% endraw %}
{% endraw %}
```

#### 4.2 Client-side Performance Optimizations
```typescript
{% raw %}
{% raw %}
// packages/client/src/hooks/useCollaborationOptimized.ts
import { useCallback, useRef, useMemo } from 'react';
import { useQuery, useMutation, useSubscription } from '@apollo/client';
import { debounce, throttle } from 'lodash';
import { OperationalTransform } from '../utils/operationalTransform';

export const useCollaborationOptimized = (documentId: string, userId: string) => {
  const operationQueueRef = useRef<any[]>([]);
  const pendingOperationsRef = useRef<Map<string, any>>(new Map());
  const lastSyncedVersionRef = useRef(0);

  // Memoized queries and mutations
  const { data, loading } = useQuery(GET_DOCUMENT, {
    variables: { id: documentId },
    fetchPolicy: 'cache-first', // Use cache when possible
  });

  const [applyOperationMutation] = useMutation(APPLY_OPERATION, {
    // Batch operations to reduce server load
    errorPolicy: 'all',
  });

  // Throttled operation sender to batch rapid changes
  const sendOperation = useCallback(
    throttle(async (operations: any[]) => {
      if (operations.length === 0) return;

      // Batch multiple operations into one request
      const batchedOperation = OperationalTransform.compose(operations);
      
      try {
        await Promise.all(
          batchedOperation.map(op => 
            applyOperationMutation({
              variables: { input: op },
              optimisticResponse: {
                applyOperation: {
                  __typename: 'OperationResult',
                  success: true,
                  operation: {
                    __typename: 'Operation',
                    id: `temp-${Date.now()}`,
                    ...op,
                    timestamp: new Date().toISOString(),
                  },
                },
              },
            })
          )
        );
        
        // Clear successfully sent operations
        operationQueueRef.current = [];
      } catch (error) {
        console.error('Batch operation failed:', error);
      }
    }, 100), // Batch operations within 100ms
    [applyOperationMutation]
  );

  // Efficient subscription handling
  useSubscription(OPERATION_ADDED, {
    variables: { documentId },
    shouldResubscribe: false, // Don't resubscribe unnecessarily
    onSubscriptionData: ({ subscriptionData }) => {
      const operation = subscriptionData.data?.operationAdded;
      if (operation && operation.authorId !== userId) {
        requestIdleCallback(() => {
          handleRemoteOperation(operation);
        });
      }
    },
  });

  const handleRemoteOperation = useCallback((operation: any) => {
    // Use requestIdleCallback for non-critical updates
    requestIdleCallback(() => {
      // Transform and apply operation
      const transformedOp = transformAgainstPending(operation);
      applyOperationToDocument(transformedOp);
    });
  }, []);

  // Memoized transform function
  const transformAgainstPending = useMemo(() => {
    return (remoteOp: any) => {
      let transformed = remoteOp;
      for (const pendingOp of operationQueueRef.current) {
        transformed = OperationalTransform.transform(transformed, pendingOp);
      }
      return transformed;
    };
  }, []);

  // Optimized document update
  const applyOperationToDocument = useCallback((operation: any) => {
    // Use functional update to avoid unnecessary re-renders
    setDocumentContent(current => 
      OperationalTransform.apply(current, operation)
    );
  }, []);

  return {
    document: data?.document,
    loading,
    sendOperation: (operation: any) => {
      operationQueueRef.current.push(operation);
      sendOperation(operationQueueRef.current);
    },
    // ... other methods
  };
};
{% endraw %}
{% endraw %}
```

---

## 🧪 Testing Your Implementation

### Testing Checklist

#### GraphQL Server ✅
- [ ] Schema validation and type safety
- [ ] Real-time subscriptions work correctly
- [ ] Operational transform handles conflicts
- [ ] MongoDB operations are efficient
- [ ] Redis caching improves performance

#### Real-time Collaboration ✅
- [ ] Multiple users can edit simultaneously
- [ ] Cursor positions sync correctly
- [ ] Text changes propagate in real-time
- [ ] Conflict resolution works properly
- [ ] Presence indicators show accurately

#### Advanced Features ✅
- [ ] Comment system functions correctly
- [ ] Version history tracks changes
- [ ] Performance optimizations reduce latency
- [ ] Offline support handles disconnections
- [ ] Security prevents unauthorized access

#### Client Performance ✅
- [ ] Apollo Client cache works efficiently
- [ ] Optimistic updates feel responsive
- [ ] Batching reduces server requests
- [ ] Memory usage stays reasonable
- [ ] UI remains responsive under load

---

## 🎯 Learning Objectives

### After completing this project, you should understand:

1. **GraphQL Architecture**
   - Advanced schema design patterns
   - Real-time subscriptions
   - Query optimization and caching
   - Error handling and validation

2. **Operational Transform**
   - Conflict resolution algorithms
   - Text synchronization techniques
   - State consistency management
   - Performance optimization

3. **Real-time Systems**
   - WebSocket management
   - Event-driven architecture
   - Scalability considerations
   - Monitoring and debugging

4. **Advanced Apollo Client**
   - Cache management strategies
   - Optimistic updates
   - Subscription handling
   - Performance optimization

5. **Collaboration Features**
   - Presence awareness
   - Version control
   - Comment systems
   - User experience design

---

## 🚀 Next Steps

### Recommended Enhancements

1. **Add Voice/Video Integration**
   ```bash
   npm install webrtc-adapter simple-peer
   ```

2. **Implement File Sharing**
   - Upload/download functionality
   - Image embedding
   - File version control

3. **Add Mobile Support**
   ```bash
   npm install react-native-webrtc
   ```

4. **Performance Monitoring**
   ```bash
   npm install @apollo/client-react-devtools
   ```

5. **Security Enhancements**
   - Role-based access control
   - Document encryption
   - Audit logging

### Continue Learning

- **AI-Powered React Applications**: Next expert project
- **Open Source Component Libraries**: Advanced patterns
- **Production Deployment**: Scalability and monitoring

---

## 📚 Additional Resources

### GraphQL Advanced
- [GraphQL Best Practices](https://graphql.org/learn/best-practices/)
- [Apollo Server Documentation](https://www.apollographql.com/docs/apollo-server/)
- [Subscription Patterns](https://www.apollographql.com/docs/react/data/subscriptions/)

### Real-time Systems
- [Operational Transform](http://operational-transformation.github.io/)
- [Conflict-free Replicated Data Types](https://crdt.tech/)
- [WebSocket Best Practices](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API)

### Performance
- [Apollo Client Performance](https://www.apollographql.com/docs/react/performance/performance/)
- [React Performance Optimization](https://react.dev/learn/render-and-commit)

---

**Continue to**: [AI-Powered React Implementation](./04-AI-Powered-React-Implementation.md)
