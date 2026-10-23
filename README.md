# Secretaria da Ala Ipanema

Site de página única (`index.html`) com gerador de atas, calendário de domingos e acompanhamento das atualizações do Manual.

## Publicar (uma vez)

1. Crie um repositório **público** no GitHub e suba estes arquivos, mantendo as pastas.
2. **Settings → Pages:** *Deploy from a branch*, branch `main`, pasta `/ (root)`.
3. **Settings → Actions → General → Workflow permissions:** *Read and write permissions*.
4. **Actions → Verificar Manual → Run workflow** (primeira execução, à mão).
5. Domínio próprio: **Settings → Pages → Custom domain**, e o registro CNAME no DNS do domínio.

## O que o monitor faz

- Toda segunda, às 06:17 (Brasília), lê **uma vez** o Sumário de atualizações recentes, depois de conferir o `robots.txt`.
- Grava em `data/manual-status.json` só o mês mais recente, a data e um código de comparação (hash). **Nenhum texto do Manual é guardado.**
- Se a execução falhar (página mudou, idioma diferente, bloqueio), o GitHub avisa por e-mail e a página continua funcionando na conferência manual.

## Regras do projeto

- Nunca suba dados de membros ao repositório (nem privado). Backups das atas ficam em arquivo, fora do GitHub.
- O código é público de propósito: não contém dados. Os dados de cada pessoa ficam no aparelho dela.
