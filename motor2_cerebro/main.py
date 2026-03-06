import zmq
import msgpack
import time

def main():
    print("🧠 [MOTOR 2] Iniciando Cérebro Python (Modo Teste de IPC)...")
    
    # 1. Inicializa o contexto do ZeroMQ
    context = zmq.Context()
    
    # 2. Cria o socket PULL (O Sugador)
    receiver = context.socket(zmq.PULL)
    
    # 3. Conecta na mesma via expressa que o Rust criou
    ipc_path = "ipc:///tmp/shadow_weaver.sock"
    receiver.connect(ipc_path)
    
    print(f"✅ Conectado ao Motor 1 na via: {ipc_path}")
    print("⏳ Aguardando alvos da UTI...\n")
    
    # Loop infinito esperando os dados (Event Loop síncrono para o teste)
    while True:
        try:
            # Puxa os dados binários da RAM (Fica travado aqui até o Rust mandar algo)
            mensagem_binaria = receiver.recv()
            
            # Desempacota o MsgPack de volta para um Dicionário Python
            payload = msgpack.unpackb(mensagem_binaria, raw=False)
            
            # Exibe os dados mastigados!
            print(f"🎯 ALVO RECEBIDO! Carteira: {payload[0]} | Volume: {payload[1]} SOL | Timestamp: {payload[2]}")
            
        except Exception as e:
            print(f"⚠️ Erro ao processar mensagem: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()