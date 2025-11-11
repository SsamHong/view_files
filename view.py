
from pathlib import Path
import os

print( '===============================================================================' )

print( '=========================================' )

# 打印当前工作目录
print( f'当前工作目录: {os.getcwd( )}' )

print( '=========================================' )

def print_files_recursive ( path ):
  
  p = Path( path )
  if not p.exists( ) or not p.is_dir( ):
    
    print( f'错误: "{p.resolve( )}" 不存在或不是目录' )
    
    return
    
  
  for file in p.rglob( '*' ):
    
    if file.is_file( ):
      
      print( file )
      
    
  

target_path = Path( '.' ) / 'ComfyUI' / 'models'

print_files_recursive( target_path )

print( '===============================================================================' )
