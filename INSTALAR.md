# Como colocar o app da V'Sensi no ar (iPhone)

São duas partes: o **Firebase**, que guarda o login e os dados, e o **GitHub Pages**, que hospeda o app. As duas são gratuitas.

## Parte 1: Firebase (uns 10 minutos)

1. Entre em **console.firebase.google.com** com a conta Google da V'Sensi.
2. Toque em **Criar projeto**, dê o nome `vsensi-gestao`, desative o Google Analytics e toque em **Criar projeto**.
3. **Login:** no menu, vá em **Criação → Authentication → Vamos começar**. Em **Método de login**:
   - ative **E-mail/senha** e salve;
   - ative **Google**, escolha o e-mail de suporte e salve.
4. Ainda em Authentication, abra **Configurações → Domínios autorizados → Adicionar domínio** e coloque:
   `lukasoeditor-lab.github.io`
5. **Banco de dados:** vá em **Criação → Firestore Database → Criar banco de dados**. Escolha o local `southamerica-east1 (São Paulo)`, depois **modo de produção**, e crie.
6. **Regras de segurança:** no Firestore, abra a aba **Regras**, apague tudo, cole o conteúdo do arquivo [`firestore.rules`](firestore.rules) e toque em **Publicar**.
7. **Configuração do app:** toque na engrenagem → **Configurações do projeto** → em "Seus apps", toque no ícone **</>** (Web). Dê o apelido `V'Sensi` e toque em **Registrar app**. O Firebase mostra um bloco `firebaseConfig = { ... }`: copie e mande para o Claude, ou cole em [`app/firebase-config.js`](app/firebase-config.js) no lugar de `null`.

## Parte 2: GitHub Pages (2 minutos)

1. Abra **github.com/lukasoeditor-lab/editor-** → **Settings** → **Pages**.
2. Em **Source**, escolha **Deploy from a branch**.
3. Em **Branch**, escolha `ccr-12dfec0b-kx3wa9` e a pasta `/ (root)`, e toque em **Save**.
4. Em 1 ou 2 minutos o app fica no ar em:
   **https://lukasoeditor-lab.github.io/editor-/app/**

## Parte 3: instalar no iPhone

1. Abra o link acima no **Safari**.
2. Toque em **Compartilhar** (o quadrado com a seta) → **Adicionar à Tela de Início** → **Adicionar**.
3. Abra pelo ícone da V'Sensi e crie a conta (Google, e-mail ou CPF).

A **primeira conta criada vira o CEO**. Depois o CEO pode passar o cargo para outra pessoa, na tela da equipe.

## Observações

- O login com CPF não tem como recuperar a senha por e-mail. Quem puder deve usar e-mail ou Google.
- As funções são garantidas pelo servidor (arquivo `firestore.rules`): o vendedor não consegue ler as contas a pagar e a receber, nem mudar preço ou custo, mesmo fora do app.
- No plano gratuito do Firebase cabem cerca de 50 mil leituras e 20 mil gravações por dia, muito acima do que a V'Sensi usa.
