import asyncio
import zmq
import zmq.asyncio
import msgpack
import os
import time
from dotenv import load_dotenv
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed
from solders.signature import Signature
from solders.pubkey import Pubkey

# 1. O Motor de Retentativa Implacável
async def fetch_with_retry(client, signature, max_retries=10, delay=0.5):
    for tentativa in range(max_retries):
        try:
            resposta = await client.get_transaction(
                signature,
                commitment=Confirmed,
                max_supported_transaction_version=0
            )
            if resposta and resposta.value:
                return resposta.value
        except Exception:
            pass 
            
        print(f"⏳ [Tentativa {tentativa + 1}/{max_retries}] Aguardando consenso da rede...")
        await asyncio.sleep(delay)
        
    return None

# 2. A Pinça Cirúrgica
def dissecar_transacao(transacao_completa):
    try:
        contas = transacao_completa.transaction.transaction.message.account_keys
        deployer = str(contas[0])
        
        meta = transacao_completa.transaction.meta
        tokens_envolvidos = set()
        wsol = "So11111111111111111111111111111111111111112"
        
        if meta and meta.post_token_balances:
            for balanco in meta.post_token_balances:
                mint = str(balanco.mint)
                if mint != wsol:
                    tokens_envolvidos.add(mint)
                    
        lista_tokens = list(tokens_envolvidos)
        
        print("\n🕵️‍♂️ [AUTÓPSIA CONCLUÍDA]")
        print(f"👤 Deployer (Suspeito): {deployer}")
        print(f"🪙 Tokens Identificados: {lista_tokens}")
        print("==============================================================")
        
        return deployer, lista_tokens

    except Exception as e:
        print(f"⚠️ Erro ao dissecar o Raio-X: {e}")
        return None, None

# 3. A UTI (Inteligência Anti-Fraude) - Nível 1 e 2
async def investigar_deployer(client, deployer_str):
    print(f"\n🏥 [UTI ATIVADA] Puxando a capivara financeira de: {deployer_str[:8]}...")
    try:
        pubkey = Pubkey.from_string(deployer_str)
        
        # Puxamos até 100 transações para encontrar a origem (o Big Bang da carteira)
        resposta = await client.get_signatures_for_address(pubkey, limit=100)
        
        if not resposta or not resposta.value:
            print("🚨 [CABAL DETECTADA] Carteira fantasma. Nenhuma transação anterior encontrada.")
            return False
            
        assinaturas = resposta.value
        quantidade_tx = len(assinaturas)
        
        # --- NÍVEL 1: Volume de Transações (O Aquecimento) ---
        if quantidade_tx < 15:
            print(f"🚨 [CABAL DETECTADA - NÍVEL 1] Bandeira Vermelha! Carteira Descartável.")
            print(f"🩸 Motivo: Apenas {quantidade_tx} transações no histórico. Golpe amador.")
            print("🛑 RESULTADO: ALVO DESCARTADO. Protegendo capital.")
            return False

        # --- NÍVEL 2: A Idade do Financiamento Base ---
        # A última assinatura da lista retornada é a transação mais antiga (o primeiro depósito)
        primeira_tx = assinaturas[-1]
        
        if primeira_tx.block_time:
            # Calcula a idade da carteira em horas
            idade_segundos = time.time() - primeira_tx.block_time
            idade_horas = idade_segundos / 3600
            
            print(f"🕵️‍♂️ [INVESTIGAÇÃO] A carteira realizou sua primeira transação há {idade_horas:.1f} horas.")
            
            # Se a carteira foi financiada há menos de 48 horas, é a Cabal lavando dinheiro.
            if idade_horas < 48:
                print(f"🚨 [CABAL DETECTADA - NÍVEL 2] Financiamento de Corretora Recente!")
                print(f"🩸 Motivo: Dinheiro muito fresco. A carteira foi criada especificamente para este lançamento.")
                print("🛑 RESULTADO: ALVO DESCARTADO. Protegendo capital.")
                return False
                
        # Se passou pelos dois filtros, o cara é legítimo
        print(f"✅ [LANÇAMENTO LIMPO] Desenvolvedor orgânico. Histórico estruturado e conta madura.")
        print("🟢 RESULTADO: SINAL DE COMPRA PRÉ-APROVADO.")
        return True
            
    except Exception as e:
        print(f"⚠️ Erro na UTI ao investigar o histórico: {e}")
        return False

# 4. O Cérebro Principal
async def main():
    print("🧠 [MOTOR 2] Iniciando Cérebro Analítico (UTI Dupla Blindada)...")
    
    load_dotenv()
    x_token = os.getenv("X_TOKEN")
    if not x_token:
        print("🔥 ERRO CRÍTICO: Arquivo .env não encontrado.")
        return

    rpc_url = f"https://mainnet.helius-rpc.com/?api-key={x_token}"
    solana_client = AsyncClient(rpc_url)
    print("🔗 Conectado ao RPC de Alta Performance da Solana.")

    context = zmq.asyncio.Context()
    receiver = context.socket(zmq.PULL)
    ipc_path = "ipc:///tmp/shadow_weaver.sock"
    receiver.connect(ipc_path)
    
    print(f"✅ Tubo IPC conectado em: {ipc_path}")
    print("⏳ Aguardando alvos do Motor 1...\n")

    while True:
        try:
            mensagem_binaria = await receiver.recv()
            payload = msgpack.unpackb(mensagem_binaria, raw=False)
            assinatura_str = payload[0]
            
            print(f"\n🎯 ALVO RECEBIDO! Assinatura: {assinatura_str}")
            print("🔬 Solicitando Raio-X...")

            sig_obj = Signature.from_string(assinatura_str)
            transacao_completa = await fetch_with_retry(solana_client, sig_obj)

            if transacao_completa:
                deployer, tokens = dissecar_transacao(transacao_completa)
                
                if deployer:
                    aprovado = await investigar_deployer(solana_client, deployer)
                    if aprovado:
                        print(f"🛒 [MOTOR 4 - FUTURO] Preparando ordem de compra via Jito. Token: {tokens[0] if tokens else 'Desconhecido'}")
            else:
                print(f"💀 Transação dropada pela rede.\n")

        except Exception as e:
            print(f"🔥 Erro no Event Loop: {e}")
            await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())