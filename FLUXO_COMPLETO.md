# FLUXO COMPLETO — Agente IXC

Sequência operacional ponta a ponta (fonte: operador). As **regras** que cada
passo aplica estão em `regras.md`. Este documento define a **ordem** e o
mapeamento para a máquina de estados (`agent/state.py`).

> Entrada: **patrimônio** informado pelo operador.

| # | Passo | AgentStep | Regra |
|---|-------|-----------|-------|
| 1 | Estoque → Patrimônio | CONSULTAR_PATRIMONIO | §3 |
| 2 | Exibir todos os patrimônios | CONSULTAR_PATRIMONIO | — |
| 3 | Pesquisar patrimônio (por código) | CONSULTAR_PATRIMONIO | — |
| 4 | Verificar status (Comodato / Disp. técnico / Disponível → guardar; Outro → encerrar) | CONSULTAR_PATRIMONIO | §3 |
| 5 | Abrir patrimônio | CONSULTAR_PATRIMONIO | — |
| 6 | Histórico de movimentação | VERIFICAR_MOVIMENTACAO | §4 |
| 7 | Movimentação mais recente (Comodato/Devolução; senão encerra) | VERIFICAR_MOVIMENTACAO | §4 |
| 8 | Abrir Contrato | ABRIR_CONTRATO | — |
| 9 | O.S. | VERIFICAR_NOTAS_OS | §5 |
| 10 | Verificar registros de nota (já existe p/ patrimônio → encerra) | VERIFICAR_NOTAS_OS | §5 |
| 11 | Voltar | COPIAR_CLIENTE | — |
| 12 | Cliente | COPIAR_CLIENTE | §6 |
| 13 | Copiar nome do cliente | COPIAR_CLIENTE | §6 |
| 14 | Vendas | ANALISAR_VENDAS | §7 |
| 15 | Ordenar documentos (maior → menor) | ANALISAR_VENDAS | §7 |
| 16 | Procurar documentos 638 e 641 | ANALISAR_VENDAS | §7 |
| 17 | Patrimônio corresponde? (não → encerra; sim → guardar ID produto, valor, nº NF, data emissão) | ANALISAR_VENDAS | §7 |
| 18 | Entradas | CRIAR_ENTRADA_ESTOQUE | §8 |
| 19 | Pesquisar fornecedor pelo nome do cliente | CRIAR_ENTRADA_ESTOQUE | §6 |
| 20 | Nova entrada manual | CRIAR_ENTRADA_ESTOQUE | §8 |
| 21 | Preencher campos obrigatórios | CRIAR_ENTRADA_ESTOQUE | §8 |
| 22 | Salvar | CRIAR_ENTRADA_ESTOQUE | §8 |
| 23 | Produtos | INSERIR_PRODUTOS | §9 |
| 24 | Inserir ID produto, valor, qtd=1, almoxarifado=85 | INSERIR_PRODUTOS | §9 |
| 25 | Adicionar referência (nº NF, data emissão) | INSERIR_PRODUTOS | §11 |
| 26 | Pré-DANFE | EMITIR_NFE | §10 |
| 27 | Conferir produto, valor, quantidade | EMITIR_NFE | §10 |
| 28 | Se correto → Emitir NF-e | EMITIR_NFE | §10 |
| 29 | Voltar para Contrato | FINALIZAR_OS | — |
| 30 | O.S. | FINALIZAR_OS | §12 |
| 31 | Criar nova | FINALIZAR_OS | §12 |
| 32 | Assunto = 94 | FINALIZAR_OS | §12 |
| 33 | Texto: `PATRIMÔNIO: XXXXX OK!` | FINALIZAR_OS | §12 |
| 34 | Finalizar | FINALIZAR_OS | §12 |
| 35 | Texto final: `FINALIZADO.` | FINALIZAR_OS | §12 |
| 36 | Existe outra O.S. do almoxarifado? Sim → finalizar também | FINALIZAR_OS | §12 |
| 37 | Status inicial era Comodato? Sim → abrir comodato, conferir patrimônio, devolver p/ "Meu Almoxarifado". Não → finalizar | DEVOLVER_COMODATO | §13 |

> **FIM.**

## Decisão registrada (§3)

No passo 4 continuam: **Comodato**, **Disponível técnico** e **Disponível**.
- **Disponível** → continua e **NÃO dá baixa** (confirmado pelo operador).
- Qualquer outro status → **encerrar**.
