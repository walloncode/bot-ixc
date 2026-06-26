# CONTINUAR — ponto de parada da sessão

> Atualizado sempre que o operador disser **"finalizar sessão"**.
> Última atualização: **2026-06-25**.

## Onde paramos

Implementados e testados (15 testes passando, sem browser):

- **Passos 1-5 — `CONSULTAR_PATRIMONIO`** ✅
  Botão "Exibir todos" → busca por código → Enter → lê badge de status → regra §3.
  Comodato é apenas **guardado** (`context["status_inicial_comodato"]`); devolução só no fim.
- **Passos 6-7 — `VERIFICAR_MOVIMENTACAO`** ✅
  Duplo-clique na linha do patrimônio → aba "Histórico de movimentações" →
  lê colunas `finalidade` (tipo) + `data_movimentacao` → regra §4 (mais recente
  entre Comodato/Devolução; senão ENCERRA) → segue para `ABRIR_CONTRATO`.

Sem nenhum `# CONFIRMAR` pendente nos passos já feitos.

## Próximo passo (retomar aqui)

**Passos 8-10 — Contrato → O.S. → verificar registros de nota (§5).**
Precisa do HTML real de:
1. Como **abrir o Contrato** a partir do patrimônio (link/botão/aba).
2. Onde ficam **O.S.** e **registros de nota** do contrato.
3. Como identificar se **já existe nota para o mesmo patrimônio** (§5: existe → encerra).

Regra pura `business_rules/nfe.contrato_ja_tem_nf()` já existe; falta ligar à tela.

## Mapa dos passos (ver FLUXO_COMPLETO.md)

| Passo | AgentStep | Status |
|---|---|---|
| 1-5 | CONSULTAR_PATRIMONIO | ✅ feito + testado |
| 6-7 | VERIFICAR_MOVIMENTACAO | ✅ feito + testado |
| 8 | ABRIR_CONTRATO | ⬜ próximo |
| 9-10 | VERIFICAR_NOTAS_OS | ⬜ (regra pronta) |
| 11-13 | COPIAR_CLIENTE | ⬜ |
| 14-17 | ANALISAR_VENDAS | ⬜ (regra pronta) |
| 18-22 | CRIAR_ENTRADA_ESTOQUE | ⬜ (regra pronta) |
| 23-25 | INSERIR_PRODUTOS | ⬜ |
| 26-28 | EMITIR_NFE | ⬜ (regra pronta) |
| 29-36 | FINALIZAR_OS | ⬜ |
| 37 | DEVOLVER_COMODATO | ⬜ |

## Regras pendentes de definição (não inventar — §16)

- Critério de **baixa** para status que não sejam "Disponível" (hoje `precisa_dar_baixa` → `None`).

## Como continuar tecnicamente

1. Operador envia o HTML da próxima tela.
2. Preencher seletores reais em `flows/selectors.py` (marcar incertos com `# CONFIRMAR`).
3. Ligar o passo no `flows/patrimonio.py` (`handle` + método do passo).
4. Parser puro em `flows/parsing.py` + teste offline com o HTML real em `tests/`.
5. Rodar `python -m pytest -q`.

## Setup rápido

```bash
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
pytest -q
```

---

## Convenção de commits (regra do projeto)

Commits **pequenos e atômicos**, um propósito por commit. Padrão
[Conventional Commits](https://www.conventionalcommits.org):

```
<tipo>(escopo opcional): descrição curta no imperativo
```

Tipos usados:

- **feat** — nova funcionalidade (ex.: `feat(flows): passo VERIFICAR_MOVIMENTACAO`)
- **fix** — correção de bug (ex.: `fix(patrimonio): comodato tratado no fim, não no início`)
- **chore** — manutenção/infra/config (ex.: `chore: requirements e .gitignore`)
- **test** — adicionar/ajustar testes
- **docs** — documentação (ex.: `docs: FLUXO_COMPLETO.md`)
- **refactor** — mudança interna sem alterar comportamento

Regras:
- Nada de "comitão": cada commit deve compilar e passar nos testes.
- Um commit por unidade lógica (um passo, uma regra, um fix).
- Mensagem no imperativo e em português, curta e objetiva.
