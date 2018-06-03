package net.libaoquan.trs.recommend

import org.apache.spark.SparkContext

import scala.collection.Map
import scala.collection.mutable.ArrayBuffer
import scala.util.Random
import org.apache.spark.broadcast.Broadcast
import org.apache.spark.ml.recommendation.{ALS, ALSModel}
import org.apache.spark.rdd.RDD
import org.apache.spark.sql.{DataFrame, Dataset, SparkSession}
import org.apache.spark.sql.functions._

object recommend {
  def main(args: Array[String]): Unit = {
    val sc = SparkSession.builder().appName("recommend").master("local").getOrCreate()
    SparkContext.getOrCreate().setLogLevel("WARN")
    import sc.implicits._

    val provinceToCode = Map(
      "LN" -> "10",
      "ShanX" -> "11",
      "ZJ" -> "12",
      "CQ" -> "13",
      "HLJ" -> "14",
      "AH" -> "15",
      "SanX" -> "16",
      "SD" -> "17",
      "SH" -> "18",
      "XJ" -> "19",
      "HuN" -> "20",
      "GS" -> "21",
      "HeN" -> "22",
      "BJ" -> "23",
      "NMG" -> "24",
      "YN" -> "25",
      "JX" -> "26",
      "HuB" -> "27",
      "JL" -> "28",
      "NX" -> "29",
      "TJ" -> "30",
      "FJ" -> "31",
      "SC" -> "32",
      "TW" -> "33",
      "GX" -> "34",
      "GD" -> "35",
      "HeB" -> "36",
      "HaiN" -> "37",
      "Macro" -> "38",
      "XZ" -> "39",
      "GZ" -> "40",
      "JS" -> "41",
      "QH" -> "42",
      "HK" -> "43"
    )

    val codeToProvince = Map(
      "10" -> "LN",
      "11" -> "ShanX",
      "12" -> "ZJ",
      "13" -> "CQ",
      "14" -> "HLJ",
      "15" -> "AH",
      "16" -> "SanX",
      "17" -> "SD",
      "18" -> "SH",
      "19" -> "XJ",
      "20" -> "HuN",
      "21" -> "GS",
      "22" -> "HeN",
      "23" -> "BJ",
      "24" -> "NMG",
      "25" -> "YN",
      "26" -> "JX",
      "27" -> "HuB",
      "28" -> "JL",
      "29" -> "NX",
      "30" -> "TJ",
      "31" -> "FJ",
      "32" -> "SC",
      "33" -> "TW",
      "34" -> "GX",
      "35" -> "GD",
      "36" -> "HeB",
      "37" -> "HaiN",
      "38" -> "Macro",
      "39" -> "XZ",
      "40" -> "GZ",
      "41" -> "JS",
      "42" -> "QH",
      "43" -> "HK"
    )

    def codeing(str: String): String = {
      var code: String = ""
      val Array(province, index) = str.split('_')
      code = provinceToCode(province) + index
      code
    }

    def decodeing(str: String): String = {
      var decode: String = ""
      decode = codeToProvince(str(0).toString+str(1).toString) + "_"
      for (i <- 1 to str.length-1){
        decode += str(i).toString
      }
      decode
    }

    // 加载数据
    val dataDirBase = "..\\dataset\\"
    val userIdToName = sc.read.
      textFile(dataDirBase + "user.csv").
      flatMap{ line =>
        var Array(userId, userName) = line.split(',')
        if(userId == "userId"){
          None
        } else {
          Some((userId, userName))
        }
      }.collect().toMap

    val userNameToId = sc.read.
      textFile(dataDirBase + "user.csv").
      flatMap{ line =>
        var Array(userId, userName) = line.split(',')
        if(userId == "userId"){
          None
        } else {
          Some((userName, userId))
        }
      }.collect().toMap

    val userAttractionDF = sc.read.
      textFile(dataDirBase + "user-attraction.csv").
      flatMap{ line =>
        val Array(userName, attractionId, count, rating) = line.split(',')
        if (userName == "userName"){
          None
        } else {
          Some((userNameToId(userName).toInt, codeing(attractionId).toInt, count.toInt))
        }
      }.toDF("user", "attraction", "count").cache()

    // 建立推荐模型
    val Array(trainData, cvData) = userAttractionDF.randomSplit(Array(0.9, 0.1))
    val model = new ALS().
      setSeed(Random.nextLong()).
      setImplicitPrefs(true).
      setRank(10).
      setRegParam(0.01).
      setAlpha(1.0).
      setMaxIter(5).
      setUserCol("user").
      setItemCol("attraction").
      setRatingCol("count").
      setPredictionCol("prediction").
      fit(trainData)

    // 为单个用户推荐
    def recommendByUser(userId: Int, topN: Int): Array[String] = {
      val toRecommend = model.itemFactors.
        select($"id".as("attraction")).
        withColumn("user", lit(userId))

      val topRecommendations  = model.transform(toRecommend).
        select("attraction", "prediction").
        orderBy($"prediction".desc).
        limit(topN)

      val recommends = topRecommendations.select("attraction").as[Int].collect()
      recommends.map(line => decodeing(line.toString))
    }

    // 测试推荐效果
    def testRecommend(): Double ={
      val topN = 10
      val users = cvData.select($"user").distinct().collect().map(u => u(0))
      var hit = 0.0
      var rec_count = 0.0

      for (i <- 0 to users.length-1) {
        val recs = recommendByUser(users(i).toString.toInt, topN).toSet
        val temp = trainData.select($"attraction").
          where($"user" === users(i).toString.toInt).
          collect().map(a => decodeing(a(0).toString)).
          toSet
        hit += recs.&(temp).size
        rec_count += recs.size
      }
      hit / rec_count
      /*
      val recHit = cvData.select($"user").distinct().map{ user =>
        val recs = recommendByUser(user.getInt(0), topN).toSet
        val temp = trainData.select($"attraction").
          where($"user" === user.getInt(0)).
          collect().map(a => decodeing(a(0).toString)).
          toSet
        recs.&(temp).size
      }

      val recNum = recHit.reduce(_+_)

      recNum / topN * recHit.count()
      */
    }

    testRecommend()
  }
}
