# BUSINESS_RULES.md

## 1. Objetivo do Sistema

Este sistema tem como objetivo automatizar o fluxo de emissão de NF-e no IXC, incluindo:

* Consulta de patrimônio
* Validação de contrato
* Verificação de notas fiscais existentes
* Análise de vendas
* Criação de entradas no estoque
* Emissão de NF-e
* Gestão de comodato
* Finalização de O.S.

O sistema deve seguir estritamente regras de negócio definidas abaixo, sem improvisações.

---

## 2. Princípios Gerais

* O sistema **não pode emitir NF-e sem validação completa**.
* Toda decisão deve ser baseada em dados do IXC ou regras explícitas.
* Nenhuma etapa pode ser pulada.
* Em caso de dúvida, o processo deve ser interrompido.
* IA (quando usada) nunca deve inventar dados.
* Toda ação crítica deve ser registrada em log.

---

## 3. Regras de Patrimônio

* Se o patrimônio não for encontrado → ENCERRAR PROCESSO.
* Se o patrimônio estiver em status desconhecido → ENCERRAR PROCESSO.
* Se o patrimônio estiver em:

  * Comodato → registrar status e continuar fluxo de análise.
  * Disponível técnico → registrar status e continuar fluxo de análise.
  * Disponível → registrar status e continuar fluxo de análise.
    **NÃO dar baixa** (status "Disponível" não requer baixa).

---

## 4. Regras de Movimentação

* Sempre acessar histórico de movimentação do patrimônio.

* Se não existir movimentação de:

  * Comodato
  * Devolução
    → ENCERRAR PROCESSO.

* Sempre considerar a movimentação mais recente.

---

## 5. Regras de Contrato e O.S.

* Se existir registro de NF para o mesmo patrimônio → ENCERRAR.
* Se não existir → continuar fluxo.

---

## 6. Regras de Cliente

* O nome do cliente deve ser sempre copiado do contrato.
* O nome do cliente deve ser reutilizado como fornecedor na entrada de estoque.
* Não pode haver alteração manual do nome sem validação.

---

## 7. Regras de Vendas

* As vendas devem ser filtradas por documentos:

  * 638
  * 641

* Ordenar sempre do mais recente para o mais antigo.

* O patrimônio deve bater exatamente com o patrimônio informado.

* Se não houver venda compatível → ENCERRAR PROCESSO.

* Se houver múltiplas vendas compatíveis → selecionar a mais recente.

---

## 8. Regras de Estoque / Entradas

* Sempre criar entrada manual quando o fluxo exigir.

* Campos obrigatórios:

  * Tipo de documento: 205
  * Fornecedor: cliente copiado
  * Condição de pagamento: 1
  * Data de emissão: data atual
  * Data de entrada: data atual

* Campo de observações pode ser preenchido automaticamente.

---

## 9. Regras de Produtos

* O produto deve ser exatamente o mesmo da venda.
* Quantidade padrão: 1
* Almoxarifado padrão: 85
* Preço deve ser idêntico ao da venda.
* Nunca alterar valores manualmente.

---

## 10. Regras de NF-e

* Sempre gerar Pré-DANFE antes de emitir.

* Validar:

  * Produto
  * Quantidade
  * Valor
  * Referência da venda

* Se qualquer divergência for encontrada → NÃO EMITIR.

* Se tudo estiver correto → emitir NF-e.

---

## 11. Regras de Referência Fiscal

* A NF da venda deve ser usada como referência.
* Data de emissão deve ser registrada na entrada.
* Número da NF deve ser salvo no campo de observação.

---

## 12. Regras de O.S.

* Sempre criar O.S. após emissão.

* Assunto padrão: 94

* Texto padrão:

  * "PATRIMÔNIO: XXXXX OK! ação e finalizar"

* Sempre finalizar a O.S. após criação.

* Se existir outra O.S. do almoxarifado → também finalizar.

---

## 13. Regras de Comodato

* Se o patrimônio estiver em comodato no início do fluxo:

  * Abrir comodato
  * Validar ID do roteador
  * Confirmar correspondência com patrimônio
  * Executar devolução para “Meu Almoxarifado”

* Se não estiver em comodato → ignorar etapa.

---

## 14. Regras de Erros

### Campo excede caracteres

* Cortar texto automaticamente
* Repetir operação

### Elemento não encontrado

* Realizar scroll
* Tentar novamente
* Se persistir → encerrar

### Tela diferente da esperada

* Tirar screenshot
* Registrar erro
* Pausar fluxo

---

## 15. Regras de IA (se usada)

* IA nunca pode emitir decisão final sozinha em casos críticos.

* IA deve retornar apenas:

  * ação sugerida
  * confiança
  * explicação

* IA só pode atuar em:

  * ambiguidades
  * múltiplas opções
  * erros desconhecidos

---

## 16. Regra Final

Se qualquer regra acima não cobrir o cenário:

→ O sistema deve parar e solicitar intervenção humana.
