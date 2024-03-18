# Databricks notebook source
#create a folder to load data into
dbutils.fs.mkdirs(r'dbfs:/FileStore/kha/googleplay')

# COMMAND ----------

#import functions
import pyspark
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
spark = SparkSession.builder.appName("Temp").getOrCreate()

# COMMAND ----------

#loading data
df = spark.read.load('dbfs:/FileStore/kha/googleplay/apps.csv',inferSchema=True,header=True,format='csv',sep=',')
display(df)

# COMMAND ----------

df.show()

# COMMAND ----------

df.printSchema()

# COMMAND ----------

#as the schema was not inferred properly, i had to reformat the it. Prior doing so, i drop unimportant columns
df1 = df.drop('Size','Content Rating','Last Updated','Android Ver','Current Ver')
df1.show(10)

# COMMAND ----------

df1.printSchema()
    


# COMMAND ----------

#rename column _c0
df1 = df1.withColumnRenamed('_c0','No')
df1.show()

# COMMAND ----------

#data cleaning prior to re format the column
df1 = df1.withColumn('Installs',regexp_replace(col('Installs'),"[^0-9]","")).withColumn('Price',regexp_replace(col('Price'),'[$]',''))

# COMMAND ----------

df1.show()

# COMMAND ----------

#re format datatype for columns
df1 = df1.withColumn('Rating',col('Rating').cast('double')).withColumn('Price',col('Price').cast(IntegerType())).withColumn('Reviews',col('Reviews').cast(IntegerType())).withColumn('Installs',col('Installs').cast(IntegerType()))


# COMMAND ----------

df1.printSchema()

# COMMAND ----------

df1.show()

# COMMAND ----------

#create temp view for sql query 
df1.createOrReplaceTempView('df1_temp')

# COMMAND ----------

#Top 10 reviews given to the apps
result = spark.sql("select App, sum(Reviews) as Reviews from df1_temp group by 1 order by 2 desc limit 10")
result.show()


# COMMAND ----------

# Top 10 install apps and distribution of type (free/paid)
result1 = spark.sql("select App, Type, sum(Installs) as Installs from df1_temp where Type='Free' group by 1,2 order by 3 desc limit 10")          
result1.show()         
result2 = spark.sql("select App, Type, sum(Installs) as Installs from df1_temp where Type='Paid' group by 1,2 order by 3 desc limit 10")          
result2.show()     

# COMMAND ----------

#•	Category wise distribution of installed apps
result = spark.sql("select Category, sum(Installs) as Installs from df1_temp group by 1 order by 2 desc")
result.show()

# COMMAND ----------

#Top paid apps
result = spark.sql("select App, sum(Price) as Paid_amount from df1_temp group by 1 order by 2 desc")
result.show()

# COMMAND ----------

#Top paid rating apps
result = spark.sql("select App, sum(Rating) as Rating from df1_temp where Type = 'Paid' group by 1 order by 2 desc")
result.show()
