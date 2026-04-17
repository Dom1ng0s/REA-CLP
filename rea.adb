with Ada.Text_IO; use Ada.Text_IO;

procedure Maquina_Estados_Modular is

   -- 1. TODOS OS ESTADOS DO DIAGRAMA MAPEADOS
type Estado is (
   Deslogado, Autenticando, Escolha_Perfil,
   
   -- Estados do Aluno
   Carregando_Perfil, Verifica_Interesses, Cadastrando_Interesses,
   Processando_Novos_Dados, Processando_Historico, Gerando_Recomendacoes,
   Exibindo_Recomendacoes, Acessando_REA, Avaliando_REA, Atualizando_Perfil,
   
   -- Estados do Professor
   Preenchendo_Metadados, Catalogando_REA,
   
   Sessao_Encerrada
);

Estado_Atual : Estado := Deslogado;

begin
   loop
      case Estado_Atual is
         
         -- ==============================================================
         -- [ ENTRADA & AUTENTICAÇÃO ]
         -- ==============================================================
         when Deslogado       => Estado_Atual := Autenticando;
         
         when Autenticando    => Estado_Atual := (if Credencial_Valida then Escolha_Perfil else Deslogado);
         
         when Escolha_Perfil  => Estado_Atual := (if E_Aluno then Carregando_Perfil else Preenchendo_Metadados);

         -- ==============================================================
         -- [ FLUXO DO ALUNO ]
         -- ==============================================================
         when Carregando_Perfil       => Estado_Atual := Verifica_Interesses;
         
         when Verifica_Interesses     => 
            if Tem_Interesses then
               Estado_Atual := Processando_Historico;
            else
               Estado_Atual := Cadastrando_Interesses;
            end if;
            
         when Cadastrando_Interesses  => Estado_Atual := Processando_Novos_Dados;
         when Processando_Novos_Dados => Estado_Atual := Gerando_Recomendacoes;
         when Processando_Historico   => Estado_Atual := Gerando_Recomendacoes;
         
         when Gerando_Recomendacoes   => Estado_Atual := Exibindo_Recomendacoes;
         when Exibindo_Recomendacoes  => Estado_Atual := Acessando_REA;
         when Acessando_REA           => Estado_Atual := Avaliando_REA;
         when Avaliando_REA           => Estado_Atual := Atualizando_Perfil;
         when Atualizando_Perfil      => Estado_Atual := Sessao_Encerrada;

         -- ==============================================================
         -- [ FLUXO DO PROFESSOR ]
         -- ==============================================================
         when Preenchendo_Metadados   => Estado_Atual := Catalogando_REA;
         
         when Catalogando_REA         => Estado_Atual := (if Mais_REA then Preenchendo_Metadados else Sessao_Encerrada);

         -- ==============================================================
         -- [ SAÍDA ]
         -- ==============================================================
         when Sessao_Encerrada        => exit; 

      end case;
   end loop;
   end;