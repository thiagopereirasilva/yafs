# Como Instalar YAFS Fog Simulator
 * Fazer clone do repositório [YAFS](https://github.com/acsicuib/YAFS)

 * Instalar o [conda](https://www.digitalocean.com/community/tutorials/how-to-install-anaconda-on-ubuntu-18-04-quickstart)

 * Mudar no arquivo **yafs.yml** a versão da biblioteca pyparsing para 2.4.7 (se não mudar o conda não conseguirá instalar/configurar o ambiente)

 * Executar a atualização do conda (conda update conda)

 * Criar o environment **yafs**
 ```
 (base) … /YAFS$ conda env update -f yafs.yml
(base) … $ conda activate yafs (Para ativar o ambiente)
(yafs) … $ conda deactivate (Para desativar o ambiente)
```
 
 * No arquivo main1.py mudar a linha 152 para: logging.config.fileConfig('/home/thiago/YAFS/src/examples/Tutorial/logging.ini')
 
 * Criar script 'run_tutorial1.sh':
```
export PYTHONPATH=$PYTHONPATH:/home/thiago/YAFS/src/:src/examples/Tutorial/ 
python2 src/examples/Tutorial/main1.py
```


 * Para executar:
```
(base) … $ conda activate yafs (Para ativar o ambiente)
(yafs) ./run_tutorial1.sh
```
 * Serão gerados dois arquivos .csv e também a topologia da rede (network.gexf)
